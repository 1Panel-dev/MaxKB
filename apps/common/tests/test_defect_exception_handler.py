import json
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError

from common.exception import handle_exception as exception_handle_module
from common.exception.app_exception import BadRequest400
from common.handle import handle_exception as common_handle_module


class ExceptionHandlerDefectTests(SimpleTestCase):
    def test_bad_request_uses_http_400(self):
        for module in (exception_handle_module, common_handle_module):
            with self.subTest(module=module.__name__):
                response = module.handle_exception(BadRequest400(400, "Invalid parameter"), {})

                self.assertEqual(400, response.status_code)
                self.assertEqual(400, json.loads(response.content)["code"])

    def test_validation_error_uses_http_400(self):
        for module in (exception_handle_module, common_handle_module):
            with self.subTest(module=module.__name__):
                response = module.handle_exception(ValidationError("Invalid parameter"), {})

                self.assertEqual(400, response.status_code)
                self.assertEqual(400, json.loads(response.content)["code"])

    def test_unhandled_exception_hides_internal_details(self):
        internal_message = "secret database path /opt/maxkb/private"

        for module in (exception_handle_module, common_handle_module):
            with (
                self.subTest(module=module.__name__),
                patch(f"{module.__name__}.maxkb_logger") as logger,
            ):
                response = module.handle_exception(RuntimeError(internal_message), {})
                payload = json.loads(response.content)

                self.assertEqual(500, response.status_code)
                self.assertEqual(500, payload["code"])
                self.assertNotIn("secret", str(payload["message"]).lower())
                self.assertNotIn("/opt/maxkb", str(payload["message"]))
                logger.error.assert_called_once()
