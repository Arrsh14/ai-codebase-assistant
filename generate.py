from google import genai
from store import collection

try:
    client = genai.Client()  # reads GEMINI_API_KEY from env automatically
except Exception as e:
    print(f"⚠️ Could not initialize Gemini client. Is GEMINI_API_KEY set? ({e})")
    client = None


def ask(question, n_results=8):
    if not question or not question.strip():
        return "⚠️ Please enter a non-empty question."

    if client is None:
        return "⚠️ Gemini client isn't set up — check your GEMINI_API_KEY."

    # Step A: retrieve
    try:
        results = collection.query(
            query_texts=[question],
            n_results=n_results,
        )
    except Exception as e:
        return f"⚠️ Error retrieving from the vector store: {e}"

    documents = results.get("documents", [[]])
    metadatas = results.get("metadatas", [[]])

    if not documents or not documents[0]:
        return "⚠️ No relevant chunks were found for this question. Try rephrasing, or check that the repo was indexed correctly."

    chunks = documents[0]
    sources = [meta["source"] for meta in metadatas[0]]

    # Step B: build a grounded prompt
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

    # Step C: generate
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        answer = response.text
    except Exception as e:
        return f"⚠️ Error generating an answer from Gemini: {e}"

    if not answer:
        return "⚠️ Gemini returned an empty response. Try again."

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
        result = ask(question)
        if result and result.startswith("⚠️"):
            print(result)