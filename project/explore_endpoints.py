#!/usr/bin/env python3
"""
Explore what's inside the SPARQL endpoints
"""

import asyncio
import httpx

async def explore_endpoints():
    print("🔬 EXPLORING SPARQL ENDPOINTS: What Data Do They Contain?")
    print("=" * 70)
    
    endpoints = [
        {
            "name": "UniProt", 
            "url": "https://sparql.uniprot.org/sparql/",
            "description": "Universal Protein Resource"
        },
        {
            "name": "Bgee", 
            "url": "https://www.bgee.org/sparql/",
            "description": "Gene Expression Database"
        },
        {
            "name": "OMA Browser", 
            "url": "https://sparql.omabrowser.org/sparql/",
            "description": "Orthologous Matrix"
        }
    ]
    
    print("\n1️⃣ WHAT ARE THESE ENDPOINTS?")
    for endpoint in endpoints:
        print(f"   🗄️  {endpoint['name']}: {endpoint['description']}")
        print(f"      URL: {endpoint['url']}")
        print(f"      Type: Live queryable biological database")
        print()
    
    print("2️⃣ WHAT DATA DO THEY CONTAIN?")
    
    print("\n   🧬 UniProt (https://sparql.uniprot.org/sparql/)")
    print("   Contains:")
    print("   • Protein sequences (amino acid chains)")
    print("   • Protein functions and annotations") 
    print("   • Gene names and synonyms")
    print("   • Taxonomic information (which species)")
    print("   • Disease associations")
    print("   • Subcellular locations")
    print("   Example: TP53 protein sequence, function as tumor suppressor")
    
    print("\n   📊 Bgee (https://www.bgee.org/sparql/)")
    print("   Contains:")
    print("   • Gene expression levels across tissues")
    print("   • Expression across developmental stages") 
    print("   • Cross-species expression comparisons")
    print("   • Anatomical ontology mappings")
    print("   Example: TP53 expression in brain vs liver across species")
    
    print("\n   🔄 OMA Browser (https://sparql.omabrowser.org/sparql/)")
    print("   Contains:")
    print("   • Orthologous relationships (same genes in different species)")
    print("   • Evolutionary relationships")
    print("   • Gene families and clusters")
    print("   • Phylogenetic information")
    print("   Example: Human TP53 ↔ Mouse Trp53 ↔ Rat Trp53 relationships")
    
    print("\n3️⃣ HOW YOUR APP ACCESSES THEM")
    print("   Your code doesn't run custom queries...")
    print("   Instead, it downloads their METADATA:")
    print("   • Example queries they support")
    print("   • Data structure descriptions (schemas)")
    print("   • What kinds of questions you can ask")
    print("   • Available data fields and relationships")
    
    print("\n4️⃣ WHAT THE LOADERS DO")
    print("   🔍 SparqlExamplesLoader:")
    print("      • Downloads example SPARQL queries")
    print("      • 'Find all proteins in human'")
    print("      • 'Get expression data for gene X'")
    print("      • 'Find orthologs of protein Y'")
    print()
    print("   🏗️  SparqlVoidShapesLoader:")
    print("      • Downloads data structure descriptions")
    print("      • 'Protein has sequence, function, location'")
    print("      • 'Gene has expression, tissue, stage'")
    print("      • 'Ortholog has species1, species2, confidence'")
    print()
    print("   ℹ️  SparqlInfoLoader:")
    print("      • Downloads general endpoint information")
    print("      • Endpoint URLs and descriptions")
    print("      • Contact information and usage guidelines")
    
    print("\n5️⃣ EXAMPLE: WHAT GETS EMBEDDED")
    sample_docs = [
        "UniProt SPARQL endpoint: Query for protein sequences, functions, and annotations",
        "Example query: SELECT ?protein ?sequence WHERE { ?protein a up:Protein ; up:sequence ?sequence }",
        "Bgee gene expression: Find expression levels across tissues and developmental stages",
        "Example query: SELECT ?gene ?tissue ?expression WHERE { ?gene bgee:expressedIn ?tissue ; bgee:level ?expression }",
        "OMA orthology: Discover evolutionary relationships between genes across species",
        "Example query: SELECT ?gene1 ?gene2 WHERE { ?gene1 oma:orthologousTo ?gene2 }"
    ]
    
    print("   Sample embedded documents:")
    for i, doc in enumerate(sample_docs, 1):
        print(f"   {i}. {doc}")
    
    print("\n6️⃣ WHY THIS IS POWERFUL")
    print("   When you ask: 'Which databases have protein sequences?'")
    print("   Your app finds: UniProt example queries about protein sequences")
    print("   Result: 'UniProt contains protein sequences - here's how to query it'")
    print()
    print("   When you ask: 'Find gene expression data'")
    print("   Your app finds: Bgee examples about expression queries")
    print("   Result: 'Bgee has expression data - here are example queries'")
    
    print("\n🎯 SUMMARY: Endpoints provide METADATA about biological databases")
    print("   Not the actual data, but information about:")
    print("   • What data they contain")
    print("   • How to query it")
    print("   • What questions you can ask")
    print("   • Example queries to get you started")

if __name__ == "__main__":
    asyncio.run(explore_endpoints())