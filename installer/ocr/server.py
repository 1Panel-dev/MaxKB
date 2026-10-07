# coding=utf-8
"""Local CPU text OCR. Paddle and PDF rendering stay outside MaxKB's environment."""

import argparse
from collections import OrderedDict
import hashlib
import io
import json
import multiprocessing as mp
import os
from pathlib import Path
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


def normalize_result(result, native_text):
    raw = result.json
    if isinstance(raw, str):
        raw = json.loads(raw)
    raw = raw.get("res", raw)
    ocr = raw
    lines = [
        {"text": text, "score": float(score), "bbox": list(box)}
        for text, score, box in zip(ocr.get("rec_texts", []), ocr.get("rec_scores", []),
                                    ocr.get("rec_boxes", []))
    ]
    return {"text": "\n".join(ocr.get("rec_texts", [])), "lines": lines, "native_text": native_text}


def parser_process(connection, model_dir):
    # Model downloads are confined to the explicit warmup step. Runtime uses the locked local models.
    os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
    from paddleocr import PaddleOCR
    from pypdf import PdfReader
    import pypdfium2 as pdfium

    model_args = {}
    if model_dir:
        config = json.loads((Path(model_dir) / "pipeline.json").read_text(encoding="utf-8"))
        model_args["paddlex_config"] = config
    pipeline = PaddleOCR(
        device="cpu", use_doc_orientation_classify=True, use_doc_unwarping=False,
        use_textline_orientation=True, text_rec_score_thresh=0.0, **model_args,
    )
    connection.send({"ready": True})
    while True:
        message = connection.recv()
        if message is None:
            break
        try:
            pdf_bytes, page_number, dpi = message
            reader = PdfReader(io.BytesIO(pdf_bytes))
            if reader.is_encrypted:
                raise ValueError("Encrypted PDF is not supported")
            native_text = reader.pages[page_number - 1].extract_text() or ""
            document = pdfium.PdfDocument(pdf_bytes)
            try:
                page = document[page_number - 1]
                try:
                    bitmap = page.render(scale=dpi / 72)
                    try:
                        picture = bitmap.to_pil().convert("RGB")
                    finally:
                        bitmap.close()
                finally:
                    page.close()
            finally:
                document.close()
            import numpy as np
            result = next(iter(pipeline.predict(input=np.asarray(picture))))
            connection.send({"result": normalize_result(result, native_text)})
        except Exception as exc:
            connection.send({"error": str(exc)[:2000]})


class Parser:
    def __init__(self, model_dir, timeout=300):
        self.model_dir, self.timeout = model_dir, timeout
        self.lock = threading.Lock()
        self.process = None
        self.connection = None
        self.ready = False
        self.queue_timeout = 300
        self.cache = OrderedDict()

    def recognize_cached(self, content, page, dpi):
        # Only one inference runs at a time; repeated previews can share its result.
        key = (hashlib.sha256(content).digest(), page, dpi)
        if not self.lock.acquire(timeout=self.queue_timeout):
            return {"busy": True}, False
        try:
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key], True
            try:
                response = self.recognize(content, page, dpi)
            except TimeoutError:
                raise
            except Exception:
                self.stop()
                raise
            if "result" in response:
                self.cache[key] = response
                if len(self.cache) > 32:
                    self.cache.popitem(last=False)
            return response, False
        finally:
            self.lock.release()

    def stop(self):
        self.ready = False
        if self.process:
            self.process.terminate()
            self.process.join(10)
            if self.process.is_alive():
                self.process.kill()
                self.process.join()
        if self.connection:
            self.connection.close()
        self.process = self.connection = None

    def start(self):
        self.stop()
        self.connection, child = mp.Pipe()
        self.process = mp.Process(target=parser_process, args=(child, self.model_dir), daemon=True)
        self.process.start()
        child.close()
        if not self.connection.poll(self.timeout):
            self.stop()
            raise TimeoutError("OCR model initialization timed out")
        if not self.connection.recv().get("ready"):
            self.stop()
            raise RuntimeError("OCR model initialization failed")
        self.ready = True

    def recognize(self, content, page, dpi):
        if not self.ready or not self.process.is_alive():
            self.start()
        self.connection.send((content, page, dpi))
        if not self.connection.poll(self.timeout):
            self.stop()
            raise TimeoutError("Page recognition exceeded 300 seconds")
        return self.connection.recv()


def model_manifest(root):
    return {str(p.relative_to(root)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file() and p.name != "manifest.json"}


def warmup(root):
    os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
    from paddleocr import PaddleOCR
    pipeline = PaddleOCR(
        device="cpu", use_doc_orientation_classify=True, use_doc_unwarping=False,
        use_textline_orientation=True, text_rec_score_thresh=0.0,
    )
    root.mkdir(parents=True, exist_ok=True)
    pipeline.export_paddlex_config_to_yaml(str(root / "pipeline.yaml"))
    import shutil
    import yaml
    config = yaml.safe_load((root / "pipeline.yaml").read_text(encoding="utf-8"))

    def localize(value):
        if isinstance(value, dict):
            name = value.get("model_name")
            if name:
                source = Path(os.environ["PADDLE_PDX_CACHE_HOME"]) / "official_models" / name
                target = root / name
                if source.is_dir():
                    shutil.copytree(source, target, dirs_exist_ok=True)
                value["model_dir"] = str(target.resolve())
            for child in value.values():
                localize(child)
        elif isinstance(value, list):
            for child in value:
                localize(child)

    localize(config)
    (root / "pipeline.json").write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "manifest.json").write_text(json.dumps(model_manifest(root), indent=2), encoding="utf-8")


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, payload):
        content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except (ConnectionError, TimeoutError):
            # A closed browser/request must not terminate the warmed OCR process.
            pass

    def authorized(self):
        import hmac
        return hmac.compare_digest(self.headers.get("Authorization", ""), f"Bearer {self.server.token}")

    def do_GET(self):
        if not self.authorized():
            return self.respond(401, {"error": "Unauthorized"})
        if self.path != "/health":
            return self.respond(404, {"error": "Not found"})
        self.respond(200, {"ready": self.server.parser.ready, "engine": "paddleocr-3.3.2/pp-ocr-v5",
                           "manifest": self.server.manifest})

    def do_POST(self):
        if not self.authorized():
            return self.respond(401, {"error": "Unauthorized"})
        parsed = urlparse(self.path)
        if parsed.path != "/recognize":
            return self.respond(404, {"error": "Not found"})
        try:
            params = parse_qs(parsed.query)
            page = int(params.get("page", ["0"])[0])
            dpi = int(params.get("dpi", ["200"])[0])
            size = int(self.headers.get("Content-Length", "0"))
            if page < 1 or dpi not in (200, 300) or not 0 < size <= self.server.max_bytes:
                return self.respond(400, {"error": "Invalid page, DPI or file size"})
        except ValueError:
            return self.respond(400, {"error": "Invalid request"})
        try:
            # Consume the PDF before responding, including busy responses. Otherwise
            # Windows can reset the connection while urllib is still uploading it.
            self.connection.settimeout(30)
            content = self.rfile.read(size)
            if len(content) != size:
                return self.respond(400, {"error": "Incomplete PDF"})
            started = time.monotonic()
            response, cached = self.server.parser.recognize_cached(content, page, dpi)
            if "busy" in response:
                return self.respond(429, {"error": "OCR queue wait exceeded 300 seconds"})
            if "error" in response:
                return self.respond(422, response)
            result = {**response["result"], "page": page, "dpi": dpi,
                      "engine": "paddleocr-3.3.2/pp-ocr-v5", "manifest": self.server.manifest,
                      "cached": cached, "elapsed_seconds": round(time.monotonic() - started, 3)}
            self.respond(200, result)
        except TimeoutError as exc:
            self.respond(504, {"error": str(exc)})
        except Exception as exc:
            self.respond(503, {"error": str(exc)[:2000]})


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--port", type=int, default=11637)
    cli.add_argument("--model-dir", type=Path, default=Path(__file__).parent / "runtime" / "text-models")
    cli.add_argument("--token-file", type=Path, default=Path(__file__).parent / "runtime" / "token")
    cli.add_argument("--warmup", action="store_true")
    cli.add_argument("--max-mb", type=int, default=100)
    args = cli.parse_args()
    os.environ.setdefault("PADDLE_PDX_CACHE_HOME", str(args.model_dir.parent / "cache"))
    os.environ.setdefault("HF_HOME", str(args.model_dir.parent / "huggingface"))
    os.environ.setdefault("MODELSCOPE_CACHE", str(args.model_dir.parent / "modelscope"))
    if args.warmup:
        warmup(args.model_dir)
        return
    token = os.environ.get("MAXKB_OCR_TOKEN", "")
    if not token:
        args.token_file.parent.mkdir(parents=True, exist_ok=True)
        if not args.token_file.exists():
            import secrets
            args.token_file.write_text(secrets.token_urlsafe(32), encoding="utf-8")
        token = args.token_file.read_text(encoding="utf-8").strip()
        if not token:
            cli.error("OCR token file is empty")
    expected = json.loads((args.model_dir / "manifest.json").read_text(encoding="utf-8"))
    if model_manifest(args.model_dir) != expected:
        cli.error("Local OCR model manifest mismatch; run warmup again")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.token = token
    server.max_bytes = args.max_mb * 1024 * 1024
    server.manifest = hashlib.sha256(json.dumps(expected, sort_keys=True).encode()).hexdigest()
    server.parser = Parser(str(args.model_dir.resolve()))
    server.parser.start()
    try:
        server.serve_forever()
    finally:
        server.parser.stop()
        server.server_close()


if __name__ == "__main__":
    mp.freeze_support()
    main()
