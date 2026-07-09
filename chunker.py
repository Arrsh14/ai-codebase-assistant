"""
Stage 2 chunker: walks a real codebase folder, filters to actual code
files, skips junk, and chunks each file's contents.

Still uses the same simple fixed-size chunking as Stage 1 — we'll swap
in smarter code-aware chunking (by function/class) later.
"""

import os

# File extensions we consider "real code" worth chunking
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css",
    ".java", ".c", ".cpp", ".h", ".go", ".rb", ".php",
    ".md", ".json", ".yaml", ".yml",
}

# Folders we never want to walk into
SKIP_DIRS = {".git", "node_modules", "venv", "__pycache__", ".idea", ".vscode"}

# Specific junk files to skip even if their extension looks fine
SKIP_FILES = {".DS_Store", ".gitignore"}


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
        start += chunk_size - overlap

    return chunks


def load_and_chunk_folder(folder_path: str):
    """
    Walks a folder (including subfolders), chunks every real code file it
    finds, and returns a list of dicts with chunk text + source metadata.
    """
    all_chunks = []
    chunk_id = 0

    for root, dirs, files in os.walk(folder_path):
        # prune junk directories in-place so os.walk skips them entirely
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in sorted(files):
            if filename in SKIP_FILES:
                continue

            ext = os.path.splitext(filename)[1]
            if ext not in CODE_EXTENSIONS:
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
            except UnicodeDecodeError:
                continue

            rel_path = os.path.relpath(filepath, folder_path)

            pieces = chunk_text(text)
            for piece in pieces:
                all_chunks.append({
                    "id": f"chunk_{chunk_id}",
                    "text": piece,
                    "source_file": rel_path,
                })
                chunk_id += 1

    return all_chunks


if __name__ == "__main__":
    chunks = load_and_chunk_folder("Arrshwebproject-main")
    print(f"Total chunks created: {len(chunks)}\n")
    for c in chunks:
        print(f"[{c['id']}] from {c['source_file']}:")
        print(f"  {c['text'][:80]}...")
        print()