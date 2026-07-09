from store import collection

test_questions = [
    "how does login work?",              # paraphrase test — no exact keyword match
    "what database do we use?",          # should hit database.txt
    "how are payments processed?",       # should hit payments.txt
    "what color is the sky?",            # miss test — nothing relevant should exist
]

for question in test_questions:
    print(f"\n{'='*60}")
    print(f"QUESTION: {question}")
    print('='*60)

    results = collection.query(
        query_texts=[question],
        n_results=3,
    )

    for rank, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ), start=1):
        print(f"\n  #{rank} — from {meta['source']} (distance={dist:.4f})")
        print(f"      {doc[:150]}...")