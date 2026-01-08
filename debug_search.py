import chromadb
import logging

# Suppress warnings
logging.getLogger("pdfminer").setLevel(logging.ERROR)

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="robotics_data")

queries = [
    "what is robotics",
    "recipe about chocolate cake",
    "how to bake a cake",
    "industrial automation"
]

print("--- Distance Analysis ---")
for q in queries:
    results = collection.query(
        query_texts=[q],
        n_results=3
    )
    print(f"\nQuery: '{q}'")
    relevant_found = False
    for i in range(len(results['documents'][0])):
        dist = results['distances'][0][i]
        doc = results['documents'][0][i][:50]
        match_type = "RELEVANT" if dist < 1.2 else "IGNORED"
        print(f"  Match {i+1}: Distance={dist:.4f} ({match_type}) | Content='{doc}...'")
