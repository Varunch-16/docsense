import os
from openai import OpenAI

from src.retrieve import retrieve_top_k

MODEL_NAME = "gpt-4o-mini"


def format_context(results) -> tuple[str, list[str]]:
    """
    Convert retrieved results into prompt context and a list of source labels.
    """
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    context_blocks = []
    source_labels = []

    for i, (doc, meta) in enumerate(zip(documents, metadatas), start=1):
        content_type = meta.get("content_type", "text")
        source_label = f"{meta['source']} | page {meta['page']} | {content_type} | chunk {meta['chunk_id']}"

        context_blocks.append(f"[Source {i}] {source_label}\n{doc}")
        source_labels.append(source_label)

    context = "\n\n".join(context_blocks)
    return context, source_labels


def deduplicate_sources(source_labels: list[str], max_sources: int = 3) -> list[str]:
    """
    Keep unique sources in original order and limit how many are shown.
    """
    unique_sources = []
    seen = set()

    for src in source_labels:
        if src not in seen:
            unique_sources.append(src)
            seen.add(src)

    return unique_sources[:max_sources]


def generate_answer(question: str, k: int = 5) -> str:
    """
    Retrieve relevant chunks and generate a grounded answer using OpenAI.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. Please set it in your terminal before running."
        )

    results = retrieve_top_k(question, k=k)
    context, source_labels = format_context(results)

    prompt = f"""
You are a document question-answering assistant.

Use ONLY the information in the provided sources to answer the user's question.
Do not mention source numbers in the answer.
Do not add a sources section yourself.
If the sources do not contain enough information, say:
"I do not have enough information in the provided documents to answer that."

Answer clearly, accurately, and naturally.

Question:
{question}

Sources:
{context}
"""

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You answer questions strictly from provided document context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    answer_text = response.choices[0].message.content.strip()
    final_sources = deduplicate_sources(source_labels, max_sources=3)
    formatted_sources = "\n".join(f"- {src}" for src in final_sources)

    return f"""{answer_text}

Sources:
{formatted_sources}"""


if __name__ == "__main__":
    question = input("Enter your question: ").strip()

    if not question:
        print("Please enter a valid question.")
    else:
        print("\n--- RAG Answer ---\n")
        answer = generate_answer(question, k=5)
        print(answer)