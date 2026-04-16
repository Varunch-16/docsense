import re
import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH = "data/processed/chroma_db"
COLLECTION_NAME = "docsense_chunks"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


def get_model():
    """
    Load embedding model from local cache.
    """
    return SentenceTransformer(EMBEDDING_MODEL_NAME, local_files_only=True)


def get_collection():
    """
    Connect to the existing ChromaDB collection.
    """
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_collection(name=COLLECTION_NAME)


def clean_preview_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def retrieve_top_k(query: str, k: int = 5):
    """
    Retrieve top-k most relevant chunks for a query.
    """
    model = get_model()
    query_embedding = model.encode(query).tolist()
    collection = get_collection()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    return results


def print_results(results, preview_chars: int = 900):
    """
    Print retrieval results in a readable format.
    """
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    print("\n--- Retrieval Results ---")

    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), start=1):
        cleaned_doc = clean_preview_text(doc)

        print(f"\nResult {i}")
        print(f"Source       : {meta['source']}")
        print(f"Page         : {meta['page']}")
        print(f"Content Type : {meta['content_type']}")
        print(f"Chunk ID     : {meta['chunk_id']}")
        if "table_id" in meta:
            print(f"Table ID     : {meta['table_id']}")
        print(f"Distance     : {dist:.4f}")
        print(f"Preview      : {cleaned_doc[:preview_chars]}...")


if __name__ == "__main__":
    query = input("Enter your question: ").strip()

    if not query:
        print("Please enter a valid question.")
    else:
        results = retrieve_top_k(query, k=5)
        print_results(results)