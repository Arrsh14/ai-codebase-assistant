"""
Stage 3 chunker: walks a real codebase folder and chunks files
intelligently based on language.
  - Python: chunked by function/class using the `ast` module (real parsing)
  - JavaScript/TypeScript: chunked by function boundaries using pattern
    matching + brace counting (heuristic, not a full parser)
  - Everything else (HTML, CSS, etc.): line-boundary chunking, same as before
"""

import os
import re
import ast

CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css",
    ".java", ".c", ".cpp", ".h", ".go", ".rb", ".php",
    ".md", ".json", ".yaml", ".yml",
}

SKIP_DIRS = {".git", "node_modules", "venv", "__pycache__", ".idea", ".vscode"}
SKIP_FILES = {".DS_Store", ".gitignore"}


# ---------- Generic fallback chunker (used for non-code files) ----------

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80):
    """Split text into overlapping chunks, snapping to newlines on both ends."""
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        if end < text_len:
            last_newline = text.rfind("\n", start, end)
            if last_newline > start + (chunk_size // 3):
                end = last_newline

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_len:
            break

        next_start = end - overlap
        if next_start > start:
            newline_after = text.find("\n", next_start)
            if newline_after != -1 and newline_after < end:
                next_start = newline_after + 1

        start = next_start

    return chunks


# ---------- Python: chunk by function/class using ast ----------

def chunk_python_code(text: str):
    """
    Uses Python's ast module to find top-level functions and classes,
    returning each as its own chunk. Falls back to chunk_text() if the
    file has a syntax error or ast parsing fails for any reason.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return chunk_text(text)

    lines = text.splitlines()
    chunks = []
    leftover_start = 0  # tracks lines not yet covered by a function/class chunk

    top_level_nodes = [
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    ]

    if not top_level_nodes:
        # no functions/classes at all (e.g. a config file) — just fall back
        return chunk_text(text)

    for node in top_level_nodes:
        # if the function/class has decorators, start from the FIRST
        # decorator's line instead of the `def`/`class` line itself
        if node.decorator_list:
            start_line = node.decorator_list[0].lineno - 1
        else:
            start_line = node.lineno - 1
        end_line = node.end_lineno         # end_lineno is inclusive

        # grab any leftover lines BEFORE this function (imports, globals, etc.)
        if start_line > leftover_start:
            leftover_text = "\n".join(lines[leftover_start:start_line]).strip()
            if leftover_text:
                chunks.append(leftover_text)

        func_text = "\n".join(lines[start_line:end_line]).strip()
        if func_text:
            chunks.append(func_text)

        leftover_start = end_line

    # grab anything left after the last function/class
    if leftover_start < len(lines):
        tail_text = "\n".join(lines[leftover_start:]).strip()
        if tail_text:
            chunks.append(tail_text)

    return chunks


# ---------- JavaScript/TypeScript: chunk by function boundaries ----------

JS_FUNCTION_PATTERNS = [
    re.compile(r'^\s*(export\s+)?(async\s+)?function\s+\w+\s*\('),
    re.compile(r'^\s*(export\s+)?const\s+\w+\s*=\s*(async\s*)?\([^)]*\)\s*=>\s*{'),
    re.compile(r'^\s*(export\s+)?const\s+\w+\s*=\s*(async\s+)?function\s*\('),
    re.compile(r'^\s*(export\s+)?class\s+\w+'),
]


def chunk_js_code(text: str):
    """
    Heuristic JS/TS chunker: scans line by line for common function/class
    declaration patterns, then uses brace counting to find where each one
    ends. Not a full parser — won't catch every possible JS style, but
    handles the common cases.
    """
    lines = text.splitlines()
    chunks = []
    i = 0
    leftover_start = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        is_func_start = any(pattern.match(line) for pattern in JS_FUNCTION_PATTERNS)

        if is_func_start:
            # flush any leftover lines before this function as their own chunk
            if i > leftover_start:
                leftover_text = "\n".join(lines[leftover_start:i]).strip()
                if leftover_text:
                    chunks.append(leftover_text)

            # walk forward counting braces to find the end of this function
            brace_count = line.count("{") - line.count("}")
            end = i
            if brace_count > 0:
                j = i + 1
                while j < n and brace_count > 0:
                    brace_count += lines[j].count("{") - lines[j].count("}")
                    j += 1
                end = j - 1
            # if brace_count never went above 0 (e.g. arrow function with no
            # braces, like `const x = () => doThing()`), just take that one line

            func_text = "\n".join(lines[i:end + 1]).strip()
            if func_text:
                chunks.append(func_text)

            leftover_start = end + 1
            i = end + 1
        else:
            i += 1

    if leftover_start < n:
        tail_text = "\n".join(lines[leftover_start:]).strip()
        if tail_text:
            chunks.append(tail_text)

    # safety net: if this heuristic found nothing useful, fall back
    if not chunks:
        return chunk_text(text)

    return chunks


# ---------- Dispatcher ----------

def chunk_file(text: str, extension: str):
    """Routes to the right chunking strategy based on file extension."""
    if extension == ".py":
        return chunk_python_code(text)
    elif extension in (".js", ".jsx", ".ts", ".tsx"):
        return chunk_js_code(text)
    else:
        return chunk_text(text)


def load_and_chunk_folder(folder_path: str):
    all_chunks = []
    chunk_id = 0

    for root, dirs, files in os.walk(folder_path):
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
            pieces = chunk_file(text, ext)

            for piece in pieces:
                all_chunks.append({
                    "id": f"chunk_{chunk_id}",
                    "text": piece,
                    "source_file": rel_path,
                })
                chunk_id += 1

    return all_chunks


if __name__ == "__main__":
    chunks = load_and_chunk_folder("microblog-main")
    print(f"Total chunks created: {len(chunks)}\n")
    for c in chunks:
        print(f"[{c['id']}] from {c['source_file']}:")
        print(f"  {c['text'][:80]}...")
        print()