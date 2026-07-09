"""
Stage 1 chunker: simple fixed-size chunking with overlap.

This is deliberately naive — it just cuts text into ~N-character pieces
with some overlap so we don't slice a sentence in half at a chunk boundary.
Later we'll replace this with smarter, code-aware chunking.
"""

import os


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80):
    """Split text into overlapping chunks of roughly chunk_size characters."""
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap  # step forward, but overlap a bit

    return chunks


def load_and_chunk_folder(folder_path: str):
    """
    Reads every .txt file in a folder, chunks it, and returns a list of
    dicts with the chunk text + metadata (which file it came from).
    """
    all_chunks = []
    chunk_id = 0

    for filename in sorted(os.listdir(folder_path)):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(folder_path, filename)
        with open(filepath, "r") as f:
            text = f.read()

        pieces = chunk_text(text)
        for piece in pieces:
            all_chunks.append({
                "id": f"chunk_{chunk_id}",
                "text": piece,
                "source_file": filename,
            })
            chunk_id += 1

    return all_chunks


if __name__ == "__main__":
    chunks = load_and_chunk_folder("sample_docs")
    print(f"Total chunks created: {len(chunks)}\n")
    for c in chunks:
        print(f"[{c['id']}] from {c['source_file']}:")
        print(f"  {c['text'][:80]}...")
        print()