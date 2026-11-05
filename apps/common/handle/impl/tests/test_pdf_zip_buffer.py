"""Regression for MaxKB #7436: PDF members inside zip have no .chunks()."""

from io import BytesIO


class _ZipLikePdf:
    """Minimal stand-in for zipfile.ZipExtFile (read-only, no chunks)."""

    def __init__(self, name: str, data: bytes):
        self.name = name
        self._buf = BytesIO(data)

    def read(self, *args, **kwargs):
        return self._buf.read(*args, **kwargs)


def test_pdf_handle_reads_via_get_buffer_without_chunks(monkeypatch, tmp_path):
    import types
    import sys

    # Avoid importing the real fitz-heavy module graph; exercise the buffer write path.
    from common.handle.impl import pdf_split_handle as mod

    calls = {}

    class FakeDoc:
        def close(self):
            pass

    def fake_open(path):
        calls["path"] = path
        with open(path, "rb") as f:
            calls["bytes"] = f.read()
        return FakeDoc()

    monkeypatch.setattr(mod.fitz, "open", fake_open)
    monkeypatch.setattr(
        mod.PdfSplitHandle,
        "handle_toc",
        staticmethod(lambda *a, **k: [{"title": "t", "content": "c"}]),
    )

    payload = b"%PDF-1.4 fake"
    file_obj = _ZipLikePdf("doc.pdf", payload)

    def get_buffer(f):
        return f.read()

    result = mod.PdfSplitHandle().handle(
        file_obj, None, False, 500, get_buffer, lambda images: None
    )

    assert result["name"] == "doc.pdf"
    assert calls["bytes"] == payload
    assert not hasattr(file_obj, "chunks")
