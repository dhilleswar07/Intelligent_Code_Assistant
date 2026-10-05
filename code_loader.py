from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".cs",
    ".go",
    ".rs",
    ".sql",
    ".html",
    ".css",
}


def load_code_files(folder_path):

    folder = Path(folder_path)

    documents = []

    for file_path in folder.rglob("*"):

        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:

            try:
                content = file_path.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

                documents.append({
                    "file_name": file_path.name,
                    "file_path": str(file_path),
                    "content": content
                })

            except Exception as e:
                print(f"Could not read {file_path}: {e}")

    return documents


def chunk_code(text, chunk_size=1000, overlap=200):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def prepare_documents(folder_path):

    files = load_code_files(folder_path)

    chunks = []

    for file in files:

        file_chunks = chunk_code(file["content"])

        for i, chunk in enumerate(file_chunks):

            chunks.append({
                "id": len(chunks),
                "file_name": file["file_name"],
                "file_path": file["file_path"],
                "chunk_index": i,
                "content": chunk
            })

    return chunks