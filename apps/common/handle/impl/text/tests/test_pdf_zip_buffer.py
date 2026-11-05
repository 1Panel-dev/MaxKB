"""Regression for #7436: zip PDF members must not require UploadedFile.chunks()."""

from io import BytesIO


class _ZipLikePdf:
    def __init__(self, name: str, data: bytes):
        self.name = name
        self._buf = BytesIO(data)

    def read(self, *args, **kwargs):
        return self._buf.read(*args, **kwargs)


def test_pdf_handle_uses_get_buffer_for_non_uploaded_file(monkeypatch):
    from common.handle.impl.text import pdf_split_handle as mod

    calls = {}

    class FakeReader:
        def __init__(self, _f):
            pass

    def fake_handle_toc(self, pdf_document, limit):
        return [{"title": "t", "content": "c"}]

    monkeypatch.setattr(mod, "PdfReader", FakeReader)
    monkeypatch.setattr(mod.PdfSplitHandle, "handle_toc", fake_handle_toc)

    payload = b"%PDF-1.4 fake"
    file_obj = _ZipLikePdf("inner.pdf", payload)

    def get_buffer(f):
        data = f.read()
        calls["data"] = data
        return data

    result = mod.PdfSplitHandle().handle(
        file_obj, None, False, 500, get_buffer, lambda images: None
    )
    assert result["name"] == "inner.pdf"
    assert calls["data"] == payload
    assert not hasattr(file_obj, "chunks")
