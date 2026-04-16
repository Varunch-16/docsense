from src.ingest import load_all_pdfs


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """
    Split text into overlapping word-based chunks.
    """
    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))

        if end >= len(words):
            break

        start = max(end - overlap, 0)

    return chunks


def chunk_records(records: list[dict], chunk_size: int = 500, overlap: int = 100) -> list[dict]:
    """
    Convert extracted records into chunk-level records while preserving metadata.
    """
    chunked_records = []

    for record in records:
        text_chunks = chunk_text(record["text"], chunk_size=chunk_size, overlap=overlap)

        for chunk_id, chunk in enumerate(text_chunks, start=1):
            chunk_record = {
                "source": record["source"],
                "page": record["page"],
                "content_type": record["content_type"],
                "chunk_id": chunk_id,
                "text": chunk,
            }

            # Preserve table_id if present
            if "table_id" in record:
                chunk_record["table_id"] = record["table_id"]

            chunked_records.append(chunk_record)

    return chunked_records


if __name__ == "__main__":
    records = load_all_pdfs("data/raw")
    chunked = chunk_records(records, chunk_size=500, overlap=100)

    print("\n--- Chunking Summary ---")
    print(f"Total extracted records: {len(records)}")
    print(f"Total chunk-level records: {len(chunked)}")

    text_chunks = sum(1 for r in chunked if r["content_type"] == "text")
    table_chunks = sum(1 for r in chunked if r["content_type"] == "table")

    print(f"Text chunks : {text_chunks}")
    print(f"Table chunks: {table_chunks}")

    if chunked:
        sample = chunked[0]
        print("\n--- Sample Chunk ---")
        print(f"Source       : {sample['source']}")
        print(f"Page         : {sample['page']}")
        print(f"Content Type : {sample['content_type']}")
        print(f"Chunk ID     : {sample['chunk_id']}")
        if "table_id" in sample:
            print(f"Table ID     : {sample['table_id']}")
        print(f"Chunk word count: {len(sample['text'].split())}")
        print(f"Text preview : {sample['text'][:1000]}...")