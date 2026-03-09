#!/usr/bin/env python3
"""
Show exactly what happens when processing endpoints
"""

import asyncio
from sparql_llm import SparqlExamplesLoader

async def show_endpoint_processing():
    print("🔬 WHAT HAPPENS INSIDE THE ENDPOINTS")
    print("=" * 50)
    
    print("\n1️⃣ LOADING REAL DATA FROM UNIPROT")
    print("   Connecting to https://sparql.uniprot.org/sparql/...")
    
    try:
        # Load real examples from UniProt
        loader = SparqlExamplesLoader("https://sparql.uniprot.org/sparql/")
        docs = loader.load()
        
        print(f"   ✅ Downloaded {len(docs)} example documents")
        
        print("\n2️⃣ SAMPLE DOCUMENTS (what gets embedded):")
        for i, doc in enumerate(docs[:3]):  # Show first 3
            print(f"\n   Document {i+1}:")
            print(f"   Content: {doc.page_content[:200]}...")
            print(f"   Metadata: {doc.metadata}")
            
        print("\n3️⃣ TYPES OF INFORMATION EXTRACTED:")
        query_types = set()
        for doc in docs[:10]:  # Look at first 10
            if 'SELECT' in doc.page_content:
                # Extract what the query is about
                content_lower = doc.page_content.lower()
                if 'protein' in content_lower:
                    query_types.add("Protein queries")
                if 'gene' in content_lower:
                    query_types.add("Gene queries")
                if 'sequence' in content_lower:
                    query_types.add("Sequence queries")
                if 'organism' in content_lower or 'species' in content_lower:
                    query_types.add("Species/organism queries")
                if 'annotation' in content_lower:
                    query_types.add("Annotation queries")
        
        print("   Types of queries found:")
        for query_type in sorted(query_types):
            print(f"   • {query_type}")
            
        print(f"\n4️⃣ HOW THIS BECOMES SEARCHABLE:")
        print("   Each document gets converted to a 384-dimensional vector")
        print("   Example process:")
        if docs:
            sample_doc = docs[0]
            print(f"   Text: '{sample_doc.page_content[:100]}...'")
            print("   ↓ (BAAI embedding)")
            print("   Vector: [-0.123, 0.456, -0.789, ..., 0.234] (384 numbers)")
            print("   ↓ (stored in Qdrant)")
            print("   Ready for similarity search!")
        
        print(f"\n5️⃣ WHAT YOUR APP CAN NOW ANSWER:")
        print("   • 'How do I query for proteins?' → Finds UniProt query examples")
        print("   • 'What SPARQL queries exist?' → Finds all example queries")
        print("   • 'How to get protein sequences?' → Finds sequence-related examples")
        print("   • 'UniProt endpoint information' → Finds UniProt metadata")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   (This might happen if the endpoint is slow or unavailable)")

if __name__ == "__main__":
    asyncio.run(show_endpoint_processing())