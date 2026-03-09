#!/usr/bin/env python3
"""
Demo: How embedding search narrows down databases
"""

import asyncio
import numpy as np
from fastembed import TextEmbedding
import httpx

async def demo_embedding_search():
    print("🔍 EMBEDDING SEARCH DEMO: How Question Narrows Database Results")
    print("=" * 70)
    
    # Initialize embedding model
    embedding_model = TextEmbedding("BAAI/bge-small-en-v1.5")
    
    # 1. Your question
    question = "Which databases are available for protein structure?"
    print(f"\n1️⃣ USER QUESTION:")
    print(f"   '{question}'")
    
    # 2. Embed the question
    question_embedding = list(embedding_model.embed([question]))[0]
    print(f"\n2️⃣ QUESTION EMBEDDED TO VECTOR:")
    print(f"   [{question_embedding[0]:.3f}, {question_embedding[1]:.3f}, {question_embedding[2]:.3f}, ..., {question_embedding[-1]:.3f}]")
    print(f"   (384 dimensions total)")
    
    # 3. Sample database descriptions (from real SIB data)
    databases = [
        ("PDB", "Protein Data Bank: 3D structures of proteins and nucleic acids"),
        ("UniProt", "Universal Protein Resource: protein sequence and annotation data"),
        ("ChEMBL", "Database of bioactive drug-like small molecules"),
        ("Ensembl", "Genome browser for vertebrate genomes and comparative genomics"),
        ("SWISS-MODEL", "Protein structure homology-modeling server"),
        ("AlphaFold", "Protein structure database with AI-predicted structures"),
        ("GEO", "Gene Expression Omnibus: functional genomics data repository"),
        ("InterPro", "Protein families, domains and functional sites")
    ]
    
    print(f"\n3️⃣ SAMPLE DATABASES TO SEARCH:")
    for name, desc in databases:
        print(f"   • {name}: {desc}")
    
    # 4. Embed all database descriptions
    descriptions = [desc for name, desc in databases]
    db_embeddings = list(embedding_model.embed(descriptions))
    
    print(f"\n4️⃣ DATABASES CONVERTED TO VECTORS:")
    for i, (name, desc) in enumerate(databases):
        vector = db_embeddings[i]
        print(f"   {name}: [{vector[0]:.3f}, {vector[1]:.3f}, {vector[2]:.3f}, ..., {vector[-1]:.3f}]")
    
    # 5. Calculate similarities
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    print(f"\n5️⃣ SIMILARITY SCORES (Higher = More Relevant):")
    similarities = []
    for i, (name, desc) in enumerate(databases):
        similarity = cosine_similarity(question_embedding, db_embeddings[i])
        similarities.append((name, similarity, desc))
        print(f"   {name:12}: {similarity:.3f}")
    
    # 6. Sort by similarity (highest first)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n6️⃣ RANKED RESULTS (Most Relevant First):")
    print("   🏆 TOP MATCHES:")
    for i, (name, score, desc) in enumerate(similarities[:3]):
        print(f"   {i+1}. {name} (score: {score:.3f})")
        print(f"      → {desc}")
        print()
    
    print("   📉 LOWER MATCHES:")
    for i, (name, score, desc) in enumerate(similarities[3:], 4):
        print(f"   {i}. {name} (score: {score:.3f})")
    
    print(f"\n🎯 RESULT: Search narrowed from {len(databases)} databases to top 3 relevant ones!")
    print("   ✅ PDB, SWISS-MODEL, AlphaFold = protein structure databases")
    print("   ❌ GEO, Ensembl, ChEMBL = less relevant for structure questions")
    
    print("\n💡 THIS IS WHY EMBEDDING SEARCH IS POWERFUL:")
    print("   • Understands 'protein structure' ≈ '3D structure' ≈ 'homology modeling'")
    print("   • No exact keyword matching required")
    print("   • Captures semantic meaning, not just word overlap")
    print("   • Works with synonyms and scientific terminology")

if __name__ == "__main__":
    asyncio.run(demo_embedding_search())