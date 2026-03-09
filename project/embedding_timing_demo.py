#!/usr/bin/env python3
"""
Demonstrate the difference between one-time and per-query embeddings
"""

import asyncio
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
import time

async def demonstrate_embedding_timing():
    print("⏰ EMBEDDING TIMING: One-Time vs Per-Query")
    print("=" * 60)
    
    embedding_model = TextEmbedding("BAAI/bge-small-en-v1.5")
    
    print("\n1️⃣ ONE-TIME EMBEDDINGS (Database Setup)")
    print("   This happens when your app starts:")
    
    # Simulate database documents (like your SPARQL endpoint data)
    database_docs = [
        "UniProt SPARQL endpoint provides protein sequence and annotation data",
        "Bgee contains gene expression data across tissues and developmental stages",
        "OMA Browser offers orthologous relationships between genes across species",
        "SPARQL query examples for finding human proteins with specific functions",
        "Data schema describing protein structure, sequence, and functional annotations"
    ]
    
    print(f"   📚 Documents to embed: {len(database_docs)}")
    
    start_time = time.time()
    doc_embeddings = list(embedding_model.embed(database_docs))
    setup_time = time.time() - start_time
    
    print(f"   ⏱️  Time taken: {setup_time:.2f} seconds")
    print(f"   💾 Result: {len(doc_embeddings)} vectors stored permanently")
    print(f"   🔄 Frequency: Only once (or when data changes)")
    
    print("\n2️⃣ PER-QUERY EMBEDDINGS (Every User Question)")
    print("   This happens for EVERY user question:")
    
    user_questions = [
        "Which databases have protein sequences?",
        "How do I find gene expression data?", 
        "What are orthologous relationships?",
        "Show me SPARQL query examples",
        "Where can I find protein structure data?"
    ]
    
    query_times = []
    for i, question in enumerate(user_questions, 1):
        print(f"\n   Question {i}: '{question}'")
        
        start_time = time.time()
        question_embedding = list(embedding_model.embed([question]))[0]
        query_time = time.time() - start_time
        query_times.append(query_time)
        
        print(f"   ⏱️  Embedding time: {query_time:.3f} seconds")
        print(f"   🎯 Vector: [{question_embedding[0]:.3f}, {question_embedding[1]:.3f}, ..., {question_embedding[-1]:.3f}]")
        
        # Simulate finding most similar document
        similarities = []
        for j, doc_embed in enumerate(doc_embeddings):
            # Simple dot product for similarity (simplified)
            similarity = sum(a * b for a, b in zip(question_embedding[:10], doc_embed[:10]))
            similarities.append((j, similarity, database_docs[j][:50] + "..."))
        
        best_match = max(similarities, key=lambda x: x[1])
        print(f"   🎯 Best match: {best_match[2]} (similarity: {best_match[1]:.3f})")
    
    avg_query_time = sum(query_times) / len(query_times)
    print(f"\n3️⃣ TIMING COMPARISON")
    print(f"   📊 Database setup (one-time): {setup_time:.2f} seconds")
    print(f"   📊 Average query embedding: {avg_query_time:.3f} seconds")
    print(f"   📊 Ratio: Setup is {setup_time/avg_query_time:.1f}x slower than single query")
    
    print(f"\n4️⃣ WHY THIS DESIGN IS EFFICIENT")
    print("   ✅ Heavy work (384 documents) done once at startup")
    print("   ✅ Light work (1 question) done per query")
    print("   ✅ Database vectors reused for all questions")
    print("   ✅ Only question embedding changes per query")
    
    print(f"\n5️⃣ IN YOUR APP:")
    print("   🔧 index_endpoints() → One-time embedding of all database docs")
    print("   🔧 User asks question → Quick embedding of just that question")
    print("   🔧 Vector search → Compare question vector vs stored doc vectors")
    print("   🔧 Result → Relevant database info for the LLM")

if __name__ == "__main__":
    asyncio.run(demonstrate_embedding_timing())