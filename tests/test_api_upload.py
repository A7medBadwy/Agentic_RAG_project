from fastapi.testclient import TestClient

from app.api import routes
from app.main import app


def test_upload_indexes_txt_file(monkeypatch):
    chunks = [{
        "id": "point-id",
        "document_id": "document-id",
        "document_name": "notes.txt",
        "text": "Example document content",
    }]
    indexed = []

    def fake_process_file(path, original_name):
        assert path.suffix == ".txt"
        assert path.read_text(encoding="utf-8") == "Example document content"
        assert original_name == "notes.txt"
        return chunks

    monkeypatch.setattr(routes, "process_file", fake_process_file)
    monkeypatch.setattr(routes, "upsert_chunks", indexed.extend)

    response = TestClient(app).post(
        "/api/upload",
        files=[("files", ("notes.txt", "Example document content", "text/plain"))],
    )

    assert response.status_code == 200
    assert response.json() == {
        "uploaded": [{
            "filename": "notes.txt",
            "document_id": "document-id",
            "chunks_indexed": 1,
        }]
    }
    assert indexed == chunks
