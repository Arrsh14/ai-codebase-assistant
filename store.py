import chromadb
from chunker import load_and_chunk_folder

# 1. Persistent client — writes to disk so we don't re-embed every run
client = chromadb.PersistentClient(path="./chroma_db")

# 2. Create (or get) a collection — think "table for vectors"
collection = client.get_or_create_collection(name="codebase_chunks")


def build_store(folder="sample_docs"):
    chunks = load_and_chunk_folder(folder)

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        # your chunker.py actually returns: {"id": ..., "text": ..., "source_file": ...}
        ids.append(chunk["id"])
        documents.append(chunk["text"])
        metadatas.append({"source": chunk["source_file"]})

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"Stored {len(documents)} chunks in ChromaDB.")


def query_store(question, n_results=2):
    results = collection.query(
        query_texts=[question],
        n_results=n_results,
    )

    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        print(f"\n--- from {meta['source']} (distance={dist:.4f}) ---")
        print(doc[:200], "...")

if __name__ == "__main__":
    build_store(folder="Arrshwebproject-main")
    print("\n=== Test query ===")
    query_store("how does the event registration form work?")