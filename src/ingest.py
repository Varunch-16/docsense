from pathlib import Path
import re

import fitz  # PyMuPDF
import pdfplumber


def clean_text(text: str) -> str:
    """
    Basic cleanup for extracted PDF text.
    """
    if not text:
        return ""

    # Fix broken hyphenation across line breaks
    text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def table_to_text(table: list[list[str]]) -> str:
    """
    Convert a pdfplumber table (list of rows) into pipe-separated text.
    """
    lines = []
    for row in table:
        cleaned_row = []
        for cell in row:
            cell = cell if cell is not None else ""
            cell = re.sub(r"\s+", " ", str(cell)).strip()
            cleaned_row.append(cell)
        if any(cell for cell in cleaned_row):
            lines.append(" | ".join(cleaned_row))
    return "\n".join(lines)


def extract_text_records(pdf_path: Path) -> list[dict]:
    """
    Extract page text using PyMuPDF.
    """
    records = []
    doc = fitz.open(pdf_path)

    for page_index, page in enumerate(doc, start=1):
        raw_text = page.get_text("text")
        cleaned = clean_text(raw_text)

        if cleaned:
            records.append(
                {
                    "source": pdf_path.name,
                    "page": page_index,
                    "content_type": "text",
                    "text": cleaned,
                }
            )

    return records


def extract_table_records(pdf_path: Path) -> list[dict]:
    """
    Extract tables page by page using pdfplumber.
    """
    records = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            try:
                tables = page.extract_tables()
            except Exception:
                tables = []

            for table_num, table in enumerate(tables, start=1):
                table_text = table_to_text(table)
                table_text = clean_text(table_text)

                if table_text:
                    records.append(
                        {
                            "source": pdf_path.name,
                            "page": page_index,
                            "content_type": "table",
                            "table_id": table_num,
                            "text": table_text,
                        }
                    )

    return records


def load_all_pdfs(data_dir: str = "data/raw") -> list[dict]:
    """
    Read all PDFs and return both text and table records.
    """
    folder = Path(data_dir)
    if not folder.exists():
        raise FileNotFoundError(f"Data folder not found: {folder}")

    pdf_files = sorted(folder.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in: {folder}")

    all_records = []

    print(f"Found {len(pdf_files)} PDF file(s) in {folder}.")

    for pdf_file in pdf_files:
        text_records = extract_text_records(pdf_file)
        table_records = extract_table_records(pdf_file)

        all_records.extend(text_records)
        all_records.extend(table_records)

        print(
            f"Processed {pdf_file.name}: "
            f"text records = {len(text_records)}, "
            f"table records = {len(table_records)}"
        )

    return all_records


if __name__ == "__main__":
    records = load_all_pdfs()

    print("\n--- Summary ---")
    print(f"Total extracted records: {len(records)}")

    text_count = sum(1 for r in records if r["content_type"] == "text")
    table_count = sum(1 for r in records if r["content_type"] == "table")

    print(f"Text records : {text_count}")
    print(f"Table records: {table_count}")

    if records:
        sample = records[0]
        print("\n--- Sample Record ---")
        print(f"Source       : {sample['source']}")
        print(f"Page         : {sample['page']}")
        print(f"Content Type : {sample['content_type']}")
        if "table_id" in sample:
            print(f"Table ID     : {sample['table_id']}")
        print(f"Text preview : {sample['text'][:1000]}...")