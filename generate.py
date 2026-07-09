from google import genai
from store import collection

client = genai.Client()  # reads GEMINI_API_KEY from env automatically


def ask(question, n_results=3):
    # Step A: retrieve — unchanged from Step 3
    results = collection.query(
        query_texts=[question],
        n_results=n_results,
    )

    chunks = results["documents"][0]
    sources = [meta["source"] for meta in results["metadatas"][0]]

    # Step B: build a grounded prompt — unchanged logic
    context = "\n\n".join(
        f"[From {src}]\n{chunk}" for src, chunk in zip(sources, chunks)
    )

    prompt = f"""You are a codebase assistant. Answer the question using ONLY the context below.
If the context doesn't contain the answer, say so — don't make things up.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""

    # Step C: generate — this is the only part that changed
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    answer = response.text

    print(f"\nQUESTION: {question}")
    print(f"\nANSWER:\n{answer}")
    print(f"\nSOURCES: {set(sources)}")

    return answer


if __name__ == "__main__":
    print("RAG Codebase Assistant — type 'quit' to exit\n")
    while True:
        question = input("Ask a question: ")
        if question.lower() in ("quit", "exit"):
            break
        ask(question)