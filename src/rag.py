import os
import requests

from src.retrieve import retrieve_top_k

MODEL_NAME = "gpt-4o-mini"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def format_context(results):
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    context_blocks = []
    source_labels = []

    for i, (doc, meta) in enumerate(zip(documents, metadatas), start=1):
        content_type = meta.get("content_type", "text")
        source_label = (
            f"{meta['source']} | page {meta['page']} | "
            f"{content_type} | chunk {meta['chunk_id']}"
        )

        context_blocks.append(f"[Source {i}] {source_label}\n{doc}")
        source_labels.append(source_label)

    return "\n\n".join(context_blocks), source_labels


def deduplicate_sources(source_labels, max_sources=3):
    unique = []
    seen = set()

    for src in source_labels:
        if src not in seen:
            unique.append(src)
            seen.add(src)

    return unique[:max_sources]


def call_openai(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. Please set it in your terminal before running."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": "You answer questions strictly from provided document context.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.2,
    }

    response = requests.post(
        OPENAI_URL,
        headers=headers,
        json=payload,
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(f"OpenAI API error: {response.status_code} - {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def generate_answer(question: str, k: int = 5) -> str:
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

    answer_text = call_openai(prompt)

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
