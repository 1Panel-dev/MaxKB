# coding=utf-8
"""HTTP regression checks without Paddle models or private documents."""
import json
import http.client
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from server import Handler, Parser


class FakeParser(Parser):
    def __init__(self):
        super().__init__(None)
        self.ready = True
        self.calls = 0
        self.stops = 0
        self.started = threading.Event()
        self.release = threading.Event()
        self.release.set()
        self.response = {"result": {"text": "policy text", "lines": []}}

    def recognize(self, content, page, dpi):
        self.calls += 1
        self.started.set()
        if not self.release.wait(5):
            raise TimeoutError("Test request timed out")
        return self.response

    def stop(self):
        self.stops += 1


class QuietHandler(Handler):
    def log_message(self, *args):
        pass


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        self.server.token = "test-token"
        self.server.manifest = "test-models"
        self.server.max_bytes = 32 * 1024 * 1024
        self.server.parser = FakeParser()
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}/recognize?page=1&dpi=200"

    def tearDown(self):
        self.server.parser.release.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def recognize(self, content=b"fake PDF"):
        request = Request(self.url, data=content, headers={"Authorization": "Bearer test-token"})
        with urlopen(request, timeout=10) as response:
            return json.load(response)

    def test_busy_large_upload_receives_http_error_instead_of_connection_reset(self):
        parser = self.server.parser
        parser.queue_timeout = 0
        parser.lock.acquire()
        try:
            with self.assertRaises(HTTPError) as caught:
                self.recognize(b"x" * 16 * 1024 * 1024)
            self.assertEqual(caught.exception.code, 429)
            caught.exception.close()
        finally:
            parser.lock.release()
        self.assertEqual(parser.stops, 0)

    def test_overlapping_identical_previews_share_one_recognition(self):
        parser = self.server.parser
        parser.release.clear()
        with ThreadPoolExecutor(max_workers=2) as executor:
            first = executor.submit(self.recognize)
            self.assertTrue(parser.started.wait(2))
            second = executor.submit(self.recognize)
            time.sleep(0.1)
            parser.release.set()
            responses = [first.result(), second.result()]
        self.assertEqual(parser.calls, 1)
        self.assertEqual([result["text"] for result in responses], ["policy text"] * 2)
        self.assertEqual(sum(result["cached"] for result in responses), 1)

    def test_failed_recognition_is_not_cached(self):
        parser = self.server.parser
        parser.response = {"error": "Invalid PDF"}
        for _ in range(2):
            with self.assertRaises(HTTPError) as caught:
                self.recognize()
            self.assertEqual(caught.exception.code, 422)
            caught.exception.close()
        self.assertEqual(parser.calls, 2)

    def test_changed_file_and_dpi_get_fresh_results(self):
        self.recognize(b"first")
        self.recognize(b"second")
        self.url = self.url.replace("dpi=200", "dpi=300")
        self.recognize(b"first")
        self.assertEqual(self.server.parser.calls, 3)

    def test_closed_preview_does_not_stop_ocr_or_discard_result(self):
        parser = self.server.parser
        parser.release.clear()
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=10)
        connection.request("POST", "/recognize?page=1&dpi=200", b"fake PDF",
                           {"Authorization": "Bearer test-token"})
        self.assertTrue(parser.started.wait(2))
        connection.close()
        parser.release.set()
        result = self.recognize()
        self.assertEqual(result["text"], "policy text")
        self.assertTrue(result["cached"])
        self.assertEqual(parser.calls, 1)
        self.assertEqual(parser.stops, 0)


if __name__ == "__main__":
    unittest.main()
