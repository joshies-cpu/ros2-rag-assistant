import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="robotics_data")

count = collection.count()
print(f"Total documents in collection: {count}")

results = collection.get()
print(f"Document IDs: {results['ids']}")
if count > 0:
    print(f"First document length: {len(results['documents'][0])}")
    print(f"First document content preview: {results['documents'][0][:100]}")
