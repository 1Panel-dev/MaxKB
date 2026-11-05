from types import SimpleNamespace
from unittest.mock import Mock

from django.test import SimpleTestCase
from folders.serializers.resource_move import validate_edit_folder, validate_move_folder
from rest_framework.exceptions import ValidationError


class ResourceMoveValidationTests(SimpleTestCase):
    def test_unchanged_or_omitted_folder_remains_compatible_with_edit(self):
        resource = SimpleNamespace(folder_id="original")
        validate_edit_folder({}, resource)
        validate_edit_folder({"folder_id": "original", "name": "new name"}, resource)

    def test_move_rejects_empty_null_and_oversized_folder_ids_before_querying(self):
        for folder_id in ("", None, "x" * 65):
            with self.subTest(folder_id=folder_id):
                model = Mock()
                with self.assertRaises(ValidationError):
                    validate_move_folder(model, "workspace", folder_id)
                model.objects.filter.assert_not_called()
