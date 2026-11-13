import hashlib
import re
import uuid
from pathlib import Path
from typing import Iterable
import fitz
from docx import Document
from app.core.config import settings

ALLOWED = {".pdf", ".docx", ".txt"}

def extract_pages(path: Path) -> list[tuple[int, str]]:
    suffix = path.suffix.lower()
    if suffix not in ALLOWED:
        raise ValueError(f"Unsupported file type: {suffix}")
    if suffix == ".pdf":
        doc = fitz.open(path)
        return [(i + 1, page.get_text("text")) for i, page in enumerate(doc)]
    if suffix == ".docx":
        doc = Document(path)
        text = "\n".join(p.text for p in doc.paragraphs)
        for table in doc.tables:
            for row in table.rows:
                text += "\n" + " | ".join(cell.text for cell in row.cells)
        return [(1, text)]
    return [(1, path.read_text(encoding="utf-8", errors="ignore"))]

def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def chunk_text(text: str, size: int | None = None, overlap: int | None = None) -> list[str]:
    size = size or settings.chunk_size
    overlap = overlap if overlap is not None else settings.chunk_overlap
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("Require chunk_size > overlap >= 0")
    text = clean_text(text)
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start + size // 2, end)
            if boundary > start:
                end = boundary
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks

def process_file(path: Path, original_name: str) -> list[dict]:
    doc_id = hashlib.sha256(path.read_bytes()).hexdigest()
    output = []
    for page_no, page_text in extract_pages(path):
        for idx, chunk in enumerate(chunk_text(page_text)):
            output.append({
                "id": str(uuid.uuid4()),
                "document_id": doc_id,
                "document_name": original_name,
                "page_number": page_no,
                "chunk_id": f"{doc_id[:10]}-p{page_no}-c{idx}",
                "text": chunk,
                "file_type": path.suffix.lower()
            })
    return output
