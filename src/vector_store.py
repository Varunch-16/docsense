import chromadb
from sentence_transformers import SentenceTransformer

from src.ingest import load_all_pdfs
from src.chunking import chunk_records

DB_PATH = "data/processed/chroma_db"
COLLECTION_NAME = "docsense_chunks"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


def build_chunk_records() -> list[dict]:
    extracted_records = load_all_pdfs("data/raw")
    chunked_records = chunk_records(extracted_records, chunk_size=500, overlap=100)
    return chunked_records


def build_vector_store() -> None:
    chunked_records = build_chunk_records()

    print(f"\nLoading embedding model: {EMBEDDING_MODEL_NAME}")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME, local_files_only=True)

    print("Creating ChromaDB client...")
    client = chromadb.PersistentClient(path=DB_PATH)

    # Delete only the old collection, not the whole DB folder
    existing_collections = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing_collections:
        print(f"Deleting existing collection: {COLLECTION_NAME}")
        client.delete_collection(COLLECTION_NAME)

    print("Creating fresh collection...")
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    ids = []
    documents = []
    metadatas = []

    for record in chunked_records:
        chunk_uid = f"{record['source']}_p{record['page']}_{record['content_type']}_c{record['chunk_id']}"

        metadata = {
            "source": record["source"],
            "page": record["page"],
            "content_type": record["content_type"],
            "chunk_id": record["chunk_id"],
        }

        if "table_id" in record:
            metadata["table_id"] = record["table_id"]

        ids.append(chunk_uid)
        documents.append(record["text"])
        metadatas.append(metadata)

    print(f"Generating embeddings for {len(documents)} chunk(s)...")
    embeddings = model.encode(documents, show_progress_bar=True).tolist()

    print("Storing chunks in ChromaDB...")
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print("\n--- Vector Store Summary ---")
    print(f"Collection name: {COLLECTION_NAME}")
    print(f"Chunks stored   : {len(ids)}")
    print(f"DB path         : {DB_PATH}")

    text_chunks = sum(1 for m in metadatas if m["content_type"] == "text")
    table_chunks = sum(1 for m in metadatas if m["content_type"] == "table")

    print(f"Text chunks     : {text_chunks}")
    print(f"Table chunks    : {table_chunks}")

    if metadatas:
        print("\n--- Sample Stored Metadata ---")
        print(metadatas[0])