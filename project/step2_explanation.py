#!/usr/bin/env python3
"""
Step 2 Detailed Explanation: Vector Database for Biodata Search
"""

import asyncio
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import httpx

async def explain_step2():
    print("🔬 STEP 2: Vector Database for Biodata Search")
    print("=" * 60)
    
    # 1. Initialize embedding model
    print("\n1️⃣ EMBEDDING MODEL SETUP")
    embedding_model = TextEmbedding("BAAI/bge-small-en-v1.5")
    print(f"   • Model: BAAI/bge-small-en-v1.5")
    print(f"   • Dimensions: 384")
    print(f"   • Purpose: Convert biodata text → searchable vectors")
    
    # 2. Setup vector database
    print("\n2️⃣ VECTOR DATABASE SETUP")
    vectordb = QdrantClient(path="data/vectordb")
    collection_name = "sparql-docs"
    print(f"   • Database: Qdrant (local)")
    print(f"   • Location: data/vectordb/")
    print(f"   • Collection: {collection_name}")
    
    # 3. Download real biodata
    print("\n3️⃣ DOWNLOADING SIB BIODATA RESOURCES")
    response = httpx.get(
        "https://github.com/sib-swiss/sparql-llm/raw/refs/heads/main/src/expasy-agent/expasy_resources_metadata.csv", 
        follow_redirects=True
    )
    print(f"   • Source: SIB Swiss Institute of Bioinformatics")
    print(f"   • Data: Database descriptions (CSV)")
    print(f"   • Size: {len(response.text)} characters")
    
    # 4. Show sample data
    print("\n4️⃣ SAMPLE BIODATA (first 3 lines)")
    lines = response.text.split('\n')[:3]
    for i, line in enumerate(lines):
        print(f"   Line {i+1}: {line[:80]}...")
    
    # 5. Create embeddings for sample text
    print("\n5️⃣ CONVERTING TEXT TO VECTORS")
    sample_texts = [
        "UniProt: Universal Protein Resource for protein sequences",
        "PDB: Protein Data Bank for 3D molecular structures", 
        "ChEMBL: Database of bioactive drug-like molecules"
    ]
    
    for i, text in enumerate(sample_texts):
        embeddings = list(embedding_model.embed([text]))
        vector = embeddings[0]
        print(f"   Text {i+1}: {text}")
        print(f"   Vector: [{vector[0]:.3f}, {vector[1]:.3f}, {vector[2]:.3f}, ..., {vector[-1]:.3f}] (384 dims)")
        print(f"   Purpose: Enable similarity search for '{text.split(':')[0]}'")
        print()
    
    # 6. Explain the search process
    print("6️⃣ HOW SIMILARITY SEARCH WORKS")
    query = "Which databases contain protein structures?"
    query_embedding = list(embedding_model.embed([query]))[0]
    
    print(f"   User Query: '{query}'")
    print(f"   Query Vector: [{query_embedding[0]:.3f}, {query_embedding[1]:.3f}, ..., {query_embedding[-1]:.3f}]")
    print(f"   Search Process:")
    print(f"     1. Convert query → vector")
    print(f"     2. Compare with stored database vectors")
    print(f"     3. Find most similar (cosine similarity)")
    print(f"     4. Return relevant databases (PDB, AlphaFold, etc.)")
    
    print("\n7️⃣ WHAT STEP 2 ENABLES")
    print("   ✅ Semantic search: 'protein structure' finds PDB")
    print("   ✅ Fuzzy matching: 'gene expression' finds GEO, ArrayExpress")  
    print("   ✅ Multi-language: Works with scientific terminology")
    print("   ✅ Context-aware: Understands biological relationships")
    print("   ✅ Fast retrieval: Vector math is extremely fast")
    
    print("\n🎯 RESULT: Your app can now intelligently find relevant")
    print("   biological databases based on user questions!")

if __name__ == "__main__":
    asyncio.run(explain_step2())