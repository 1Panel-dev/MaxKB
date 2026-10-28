from django.test import SimpleTestCase

from application.serializers.application_api_key import EditApplicationKeySerializer


class EditApplicationKeySerializerTests(SimpleTestCase):
    def test_accepts_blank_remark(self):
        serializer = EditApplicationKeySerializer(data={"remark": ""})

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["remark"], "")
