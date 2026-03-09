import asyncio
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)

from langchain_core.language_models import BaseChatModel
import httpx

## 1. Set up LLM provider
def load_chat_model(model: str) -> BaseChatModel:
    provider, model_name = model.split("/", maxsplit=1)
    if provider == "mistralai":
        # https://python.langchain.com/docs/integrations/chat/mistralai/
        from langchain_mistralai import ChatMistralAI

        return ChatMistralAI(
            model=model_name,
            temperature=0,
            max_tokens=1024,
            
        )
    if provider == "groq":
        # https://python.langchain.com/docs/integrations/chat/groq/
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=model_name,
            temperature=0,
            max_tokens=1024,
        )
    raise ValueError(f"Unknown provider: {provider}")

llm = load_chat_model("mistralai/mistral-small-latest")
# llm = load_chat_model("groq/meta-llama/llama-4-scout-17b-16e-instruct")


## 2. Initialize vector database for similarity search, and index relevant documents


from fastembed import TextEmbedding
from qdrant_client import QdrantClient

## 2. Set up vector database for document retrieval
embedding_model = TextEmbedding("BAAI/bge-small-en-v1.5")
embedding_dimensions = 384
collection_name = "sparql-docs"
vectordb = QdrantClient(path="data/vectordb")

from langchain_core.documents import Document
from qdrant_client.http.models import Distance, VectorParams
from sparql_llm import SparqlExamplesLoader, SparqlVoidShapesLoader, SparqlInfoLoader

## 2. Set up vector database for document retrieval
endpoints: list[dict[str, str]] = [
    { "endpoint_url": "https://sparql.uniprot.org/sparql/" },
    { "endpoint_url": "https://www.bgee.org/sparql/" },
    { "endpoint_url": "https://sparql.omabrowser.org/sparql/" },
]

def index_endpoints():
    """Index SPARQL endpoints metadata in the vector database."""
    docs: list[Document] = []
    # Fetch documents from endpoints
    for endpoint in endpoints:
        logging.info(f"🔎 Retrieving metadata for {endpoint['endpoint_url']}")
        docs += SparqlExamplesLoader(
            endpoint["endpoint_url"],
            examples_file=endpoint.get("examples_file"),
        ).load()
        docs += SparqlVoidShapesLoader(
            endpoint["endpoint_url"],
            void_file=endpoint.get("void_file"),
            examples_file=endpoint.get("examples_file"),
        ).load()
    docs += SparqlInfoLoader(endpoints, source_iri="https://www.expasy.org/").load()

    # Load documents in vectordb
    if vectordb.collection_exists(collection_name):
        vectordb.delete_collection(collection_name)
    vectordb.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=embedding_dimensions, distance=Distance.COSINE),
    )
    embeddings = embedding_model.embed([q.page_content for q in docs])
    vectordb.upload_collection(
        collection_name=collection_name,
        vectors=[embed.tolist() for embed in embeddings],
        payload=[doc.metadata for doc in docs],
    )
    logging.info(f"✅ Indexed {len(docs)} documents in collection {collection_name}")


## 3. Set up document retrieval, and pass relevant context to the system prompt

from qdrant_client.models import FieldCondition, Filter, MatchValue, ScoredPoint

## 3. Set up document retrieval and system prompt
retrieved_docs_count = 3
def retrieve_docs(question: str) -> list[ScoredPoint]:
    """Retrieve documents relevant to the user's question."""
    question_embeddings = next(iter(embedding_model.embed([question])))
    retrieved_docs = vectordb.query_points(
        collection_name=collection_name,
        query=question_embeddings,
        limit=retrieved_docs_count,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="doc_type",
                    match=MatchValue(value="SPARQL endpoints query examples"),
                )
            ]
        ),
    ).points
    retrieved_docs += vectordb.query_points(
        collection_name=collection_name,
        query=question_embeddings,
        limit=retrieved_docs_count,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="doc_type",
                    match=MatchValue(value="SPARQL endpoints classes schema"),
                )
            ]
        ),
    ).points
    return retrieved_docs


def format_doc(doc: ScoredPoint) -> str:
    """Format a question/answer document to be provided as context to the model."""
    doc_lang = (
        f"sparql\n#+ endpoint: {doc.payload.get('endpoint_url', 'not provided')}"
        if "query" in doc.payload.get("doc_type", "")
        else ""
    )
    return f"\n{doc.payload['question']} ({doc.payload.get('endpoint_url', '')}):\n\n```{doc_lang}\n{doc.payload.get('answer')}\n```\n\n"

SYSTEM_PROMPT = """You are an assistant that helps users to write SPARQL queries.
Put the SPARQL query inside a markdown codeblock with the "sparql" language tag, and always add the URL of the endpoint on which the query should be executed in a comment at the start of the query inside the codeblocks starting with "#+ endpoint: " (always only 1 endpoint).
Use the queries examples and classes shapes provided in the prompt to derive your answer, don't try to create a query from nothing and do not provide a generic query.
Try to always answer with one query, if the answer lies in different endpoints, provide a federated query.
And briefly explain the query.
Here is a list of documents (reference questions and query answers, classes schema) relevant to the user question that will help you answer the user question accurately:
{relevant_docs}
"""


# async def main():
#     question = "What are the rat orthologs of human TP53?"
#     retrieved_docs = retrieve_docs(question)
#     formatted_docs = "\n".join(format_doc(doc) for doc in retrieved_docs)
#     print(formatted_docs, flush=True)
#     messages = [
#         ("system", SYSTEM_PROMPT.format(relevant_docs=formatted_docs)),
#         ("user", question),
#     ]
#     for resp in llm.stream(messages):
#         print(resp.content, end="", flush=True)
#         if resp.usage_metadata:
#             print("\n")
#             logging.info(f"🎰 {resp.usage_metadata}")


## 4. Automatically execute generated query and interpret results

from sparql_llm.validate_sparql import extract_sparql_queries
from sparql_llm.utils import query_sparql

## 4. Execute generated SPARQL query
def execute_query(last_msg: str) -> list[dict[str, str]]:
    """Extract SPARQL query from markdown and execute it."""
    for extracted_query in extract_sparql_queries(last_msg):
        if extracted_query.get("query") and extracted_query.get("endpoint_url"):
            res = query_sparql(extracted_query.get("query"), extracted_query.get("endpoint_url"))
            return res.get("results", {}).get("bindings", [])

## 5. Setup chat web UI (with Chainlit)



import json

max_try_count = 3

async def main():
    question = "What are the rat orthologs of human TP53?"
    # Retrieve relevant documents and add them to conversation
    retrieved_docs = retrieve_docs(question)
    formatted_docs = "\n".join(format_doc(doc) for doc in retrieved_docs)
    messages = [
        ("system", SYSTEM_PROMPT.format(relevant_docs=formatted_docs)),
        ("user", question),
    ]
    # Loop until query execution is successful or max tries reached
    query_success = False
    for _i in range(max_try_count):
        complete_answer = ""
        for resp in llm.stream(messages):
            print(resp.content, end="", flush=True)
            complete_answer += resp.content
            if resp.usage_metadata:
                print("\n")
                logging.info(f"🎰 {resp.usage_metadata}")

        messages.append(("assistant", complete_answer))
        if query_success:
            break

        # Run execution on the final answer
        query_res = execute_query(complete_answer)
        if len(query_res) < 1:
            logging.warning("⚠️ No results, trying to fix")
            messages.append(("user", f"""The query you provided returned no results, please fix the query:\n\n{complete_answer}"""))
        else:
            logging.info(f"✅ Got {len(query_res)} results, summarizing them")
            messages.append(("user", f"""The query you provided returned these results, summarize them:\n\n{json.dumps(query_res, indent=2)}"""))
            query_success = True
        time.sleep(1)  # Wait for a moment before retrying


# SYSTEM_PROMPT = """You are an assistant that helps users to navigate the resources and databases from the SIB Swiss Institute of Bioinformatics.
# Here is the description of resources available at the SIB:
# {context}
# Use it to answer the question"""





# if not vectordb.collection_exists(collection_name) or vectordb.get_collection(collection_name).points_count == 0:
#     index_endpoints()
# else:
#     logging.info(
#         f"ℹ️  Using existing collection '{collection_name}' with {vectordb.get_collection(collection_name).points_count} vectors"
#     )

# async def main() -> None:
#     question = "Which databases are available for protein structure?"
    
#     print(f"🤔 User Question: {question}")
    
#     # Step 3: Create fresh embedding for this question (FAST - per query)
#     print("🔄 Creating embedding for question...")
#     question_embedding = list(embedding_model.embed([question]))[0]
#     print(f"✅ Question embedded: {len(question_embedding)} dimensions")
    
#     # Step 3: Search stored database vectors (FAST - uses pre-computed vectors)
#     print("🔍 Searching for relevant database information...")
#     search_results = vectordb.search(
#         collection_name=collection_name,
#         query_vector=question_embedding.tolist(),
#         limit=3  # Get top 3 most relevant documents
#     )
    
#     print(f"📋 Found {len(search_results)} relevant documents:")
#     context_parts = []
#     for i, result in enumerate(search_results, 1):
#         score = result.score
#         metadata = result.payload
#         print(f"   {i}. Score: {score:.3f} | {metadata.get('question', 'N/A')[:80]}...")
#         context_parts.append(metadata.get('question', '') + ": " + metadata.get('answer', ''))
    
#     # Step 3: Combine relevant context
#     context = "\n\n".join(context_parts)
    
#     # Step 3: Get final answer from LLM
#     print("\n🤖 Generating response with relevant context...")
#     for resp in llm.stream(SYSTEM_PROMPT.format(context=context) + "\n\nQuestion: " + question):
#         print(resp.content, end="", flush=True)
#         if resp.usage_metadata:
#             print(f"\n\n💰 Token usage: {resp.usage_metadata}")
    
#     print("\n\n" + "="*50)
#     print("🎯 EMBEDDING SUMMARY:")
#     print("✅ Database documents: Embedded ONCE at startup (384 docs)")
#     print("✅ User question: Embedded FRESH for this query (1 question)")
#     print("✅ Vector search: Used pre-stored vectors (FAST)")
#     print("✅ Result: Relevant context for accurate answer")



    # for resp in llm.stream(SYSTEM_PROMPT.format(context=response.text) + "\n" + question):
    #     print(resp.content, end="", flush=True)
    #     if resp.usage_metadata:
    #         print(f"\n\n{resp.usage_metadata}")

# async def main():
#     question = "What are the rat orthologs of human TP53?"
#     # resp = llm.invoke(question)
#     for resp in llm.stream(question):
#         print(resp.content, end="", flush=True)
#         if resp.usage_metadata:
#             print(f"\n\n[Metadata: {resp.usage_metadata}]\n")
#     print("\n\n---\n")
#     print(resp.usage_metadata)

#     # print("=== GETTING A COMPLETE RESPONSE ===")
#     # resp = llm.invoke(question)
    
#     # print("\n🔍 **Key Response Properties:**")
#     # print(f"📝 Content: {resp.content[:100]}...")
#     # print(f"🆔 ID: {resp.id}")
#     # print(f"🏷️  Type: {resp.type}")
#     # print(f"📊 Usage Metadata: {resp.usage_metadata}")
#     # print(f"🔧 Response Metadata: {resp.response_metadata}")
    
#     # print(f"\n🛠️  **Additional Properties:**")
#     # print(f"   • additional_kwargs: {resp.additional_kwargs}")
#     # print(f"   • tool_calls: {resp.tool_calls}")
#     # print(f"   • invalid_tool_calls: {resp.invalid_tool_calls}")
    
#     # print(f"\n💡 **Useful Methods:**")
#     # print(f"   • resp.content - The main text response")
#     # print(f"   • resp.usage_metadata - Token usage info")
#     # print(f"   • resp.response_metadata - Model info & finish reason")
#     # print(f"   • resp.id - Unique response ID")
#     # print(f"   • resp.dict() - Convert to dictionary")
#     # print(f"   • resp.json() - Convert to JSON string")
    
#     # # Demonstrate some useful methods
#     # print(f"\n📋 **As Dictionary:**")
#     # resp_dict = resp.model_dump()
#     # for key, value in resp_dict.items():
#     #     if key == 'content':
#     #         print(f"   {key}: {str(value)[:50]}...")
#     #     else:
#     #         print(f"   {key}: {value}")
    
#     # print(f"\n🔗 **JSON Format:**")
#     # print(resp.model_dump_json()[:200] + "...")
    

# if __name__ == "__main__":
#     asyncio.run(main())

import chainlit as cl

@cl.on_message
async def on_message(msg: cl.Message):
    """Main function to handle when user send a message to the assistant."""
    retrieved_docs = retrieve_docs(msg.content)
    formatted_docs = "\n".join(format_doc(doc) for doc in retrieved_docs)
    async with cl.Step(name=f"{len(retrieved_docs)} relevant documents 📚️") as step:
        step.output = formatted_docs
    messages = [
        ("system", SYSTEM_PROMPT.format(relevant_docs=formatted_docs)),
        *cl.chat_context.to_openai(),
    ]

    query_success = False
    for _i in range(max_try_count):
        answer = cl.Message(content="")
        for resp in llm.stream(messages):
            await answer.stream_token(resp.content)
            if resp.usage_metadata:
                logging.info(f"🎰 {resp.usage_metadata}")
        await answer.send()

        if query_success:
            break

        query_res = execute_query(answer.content)
        if len(query_res) < 1:
            logging.warning("⚠️ No results, trying to fix")
            messages.append(("user", f"""The query you provided returned no results, please fix the query:\n\n{answer.content}"""))
        else:
            logging.info(f"✅ Got {len(query_res)} results! Summarizing them, then stopping the chat")
            async with cl.Step(name=f"{len(query_res)} query results ✨") as step:
                step.output = f"```json\n{json.dumps(query_res, indent=2)}\n```"
            messages.append(("user", f"""The query you provided returned these results, summarize them:\n\n{json.dumps(query_res, indent=2)}"""))
            query_success = True

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Rat orthologs",
            message="What are the rat orthologs of human TP53?",
        ),
    ]