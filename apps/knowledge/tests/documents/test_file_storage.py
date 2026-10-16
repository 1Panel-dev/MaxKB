"""V3 writes use OSS; existing V2 PG files remain readable."""

from contextlib import ExitStack
from io import BytesIO
from unittest.mock import MagicMock, patch
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile

from django.db import connection, transaction
from django.test import SimpleTestCase, TestCase

from common.exception.app_exception import AppApiException
from common.storage.seaweedfs import get_bucket
from common.utils.common import get_sha256_hash
from knowledge.models import File, FileSourceType, Knowledge
from knowledge.web_assets import _cache_web_image


class FileStorageTests(SimpleTestCase):
    def setUp(self):
        stack = ExitStack()
        self.addCleanup(stack.close)
        self.configured = stack.enter_context(
            patch("knowledge.models.knowledge.is_seaweedfs_enabled", return_value=True)
        )
        self.files = stack.enter_context(patch("knowledge.models.knowledge.QuerySet"))
        self.files.return_value.filter.return_value.first.return_value = None
        self.persist = stack.enter_context(patch("knowledge.models.knowledge.AppModelMixin.save"))
        self.client = stack.enter_context(patch("knowledge.models.knowledge.get_s3_client")).return_value
        stack.enter_context(patch("knowledge.models.knowledge.get_bucket", return_value="bucket"))
        self.pg = stack.enter_context(patch("knowledge.models.knowledge.select_one"))

    def test_new_images_and_documents_upload_raw_bytes_to_oss(self):
        for name in ("image.png", "guide.docx", "sheet.xlsx"):
            with self.subTest(name=name):
                file = File(file_name=name, meta={"debug": False})
                file.save(b"file bytes")

                self.assertEqual(file.storage_type, "seaweedfs")
                self.assertIsNone(file.loid)
                self.assertEqual(file.file_size, len(b"file bytes"))
                self.assertFalse(file.meta["debug"])
                self.client.put_object.assert_called_with(Bucket="bucket", Key=f"files/{file.id}", Body=b"file bytes")
                self.pg.assert_not_called()

    def test_deduplication_only_uses_oss_rows_and_preserves_the_canonical_key(self):
        for key in ("files/canonical", None):
            with self.subTest(key=key):
                existing = File(
                    id=uuid4(), storage_type="seaweedfs", file_size=7, meta={"seaweedfs_key": key} if key else {}
                )
                self.files.return_value.filter.return_value.first.return_value = existing
                file = File()

                file.save(b"content")

                self.files.return_value.filter.assert_called_with(
                    sha256_hash=get_sha256_hash(b"content"), storage_type="seaweedfs"
                )
                self.assertEqual(file.storage_type, "seaweedfs")
                self.assertIsNone(file.loid)
                self.assertEqual(file.meta["seaweedfs_key"], key or f"files/{existing.id}")
                self.client.put_object.assert_not_called()
                self.pg.assert_not_called()

    def test_missing_oss_configuration_fails_without_falling_back_to_pg(self):
        self.configured.return_value = False

        with self.assertRaises(AppApiException):
            File().save(b"content")

        self.files.assert_not_called()
        self.persist.assert_not_called()
        self.client.put_object.assert_not_called()
        self.pg.assert_not_called()

    def test_failed_oss_upload_does_not_save_a_file_record_or_use_pg(self):
        self.client.put_object.side_effect = RuntimeError("upload failed")

        with self.assertRaises(RuntimeError):
            File().save(b"content")

        self.persist.assert_not_called()
        self.pg.assert_not_called()

    def test_v2_pg_zip_files_still_read_original_bytes(self):
        archive = BytesIO()
        with ZipFile(archive, "w", ZIP_DEFLATED) as zipped:
            zipped.writestr("original.png", b"legacy image")
        file = File(storage_type="pg", loid=42, file_name="renamed.png")
        file.get_bytes_stream = MagicMock(return_value=iter([archive.getvalue()]))

        self.assertEqual(file.get_bytes(), b"legacy image")
        self.client.get_object.assert_not_called()

    def test_v2_pg_range_reads_remain_available(self):
        self.pg.side_effect = [{"chunk": b"cde"}, {"chunk": b"fg"}]

        self.assertEqual(b"".join(File(storage_type="pg", loid=42).get_bytes_stream(2, 7, 3)), b"cdefg")

        self.assertEqual([call.args[1] for call in self.pg.call_args_list], [[42, 2, 3], [42, 5, 2]])
        self.client.get_object.assert_not_called()

    def test_oss_range_reads_use_the_shared_key(self):
        file = File(storage_type="seaweedfs", meta={"seaweedfs_key": "files/canonical"})
        self.client.get_object.return_value = {"Body": BytesIO(b"cdefg")}

        self.assertEqual(b"".join(file.get_bytes_stream(2, 7, 2)), b"cdefg")

        self.client.get_object.assert_called_once_with(Bucket="bucket", Key="files/canonical", Range="bytes=2-6")
        self.pg.assert_not_called()

    @patch("common.storage.seaweedfs.CONFIG")
    def test_bucket_accepts_current_and_legacy_configuration_names(self, config):
        for values, expected in (
            ({"S3_BUCKET_NAME": "current"}, "current"),
            ({"S3_BUCKET": "legacy", "S3_BUCKET_NAME": "current"}, "legacy"),
            ({}, "maxkb"),
        ):
            with self.subTest(values=values):
                config.get.side_effect = values.get
                self.assertEqual(get_bucket(), expected)


class FileStorageDatabaseTests(TestCase):
    @patch("knowledge.models.knowledge.is_seaweedfs_enabled", return_value=True)
    @patch("knowledge.models.knowledge.get_s3_client")
    @patch("knowledge.models.knowledge.get_bucket", return_value="bucket")
    def test_same_content_as_v2_pg_file_creates_an_oss_object_and_then_reuses_oss(self, _bucket, client, _configured):
        content = b"image bytes" + uuid4().bytes
        legacy = File(storage_type="pg", loid=42, sha256_hash=get_sha256_hash(content), meta={"legacy": True})
        File.objects.bulk_create([legacy])
        image = File(file_name="image.png")
        duplicate = File(file_name="copy.png")

        image.save(content)
        duplicate.save(content)

        image.refresh_from_db()
        duplicate.refresh_from_db()
        legacy.refresh_from_db()
        self.assertEqual(image.storage_type, "seaweedfs")
        self.assertEqual(duplicate.storage_type, "seaweedfs")
        self.assertIsNone(image.loid)
        self.assertIsNone(duplicate.loid)
        self.assertEqual(image.meta["seaweedfs_key"], duplicate.meta["seaweedfs_key"])
        client.return_value.put_object.assert_called_once_with(Bucket="bucket", Key=f"files/{image.id}", Body=content)
        self.assertEqual((legacy.storage_type, legacy.loid, legacy.meta), ("pg", 42, {"legacy": True}))

    @patch("knowledge.models.knowledge.is_seaweedfs_enabled", return_value=True)
    @patch("knowledge.models.knowledge.get_s3_client")
    @patch("knowledge.web_assets.guess_image_format", return_value="png")
    @patch("knowledge.web_assets.Fork.requests_get")
    def test_web_image_cache_does_not_reuse_a_legacy_pg_image(self, fetch, _format, client, _configured):
        content = b"web image" + uuid4().bytes
        knowledge = Knowledge.objects.create(name="storage test", desc="")
        url = "https://example.test/image.png"
        legacy = File(
            storage_type="pg",
            loid=42,
            sha256_hash=get_sha256_hash(content),
            source_type=FileSourceType.KNOWLEDGE,
            source_id=str(knowledge.id),
            meta={"source_url": url},
        )
        File.objects.bulk_create([legacy])
        fetch.return_value = MagicMock(status_code=200, content=content)

        image_id = _cache_web_image(url, knowledge.id)
        cached_id = _cache_web_image(url, knowledge.id)

        self.assertIsNotNone(image_id)
        self.assertNotEqual(image_id, str(legacy.id))
        self.assertEqual(image_id, cached_id)
        image = File.objects.get(pk=image_id)
        self.assertEqual(image.storage_type, "seaweedfs")
        self.assertIsNone(image.loid)
        client.return_value.put_object.assert_called_once()

    def create_legacy_pg_files(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT lo_from_bytea(0, %s)", [b"legacy bytes"])
            loid = cursor.fetchone()[0]
        files = [File(storage_type="pg", loid=loid, meta={"original_size": len(b"legacy bytes")}) for _ in range(2)]
        File.objects.bulk_create(files)
        # Match an actual replacement, which loads persisted File instances.
        return [File.objects.get(pk=file.pk) for file in files]

    def large_object_exists(self, loid):
        with connection.cursor() as cursor:
            cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_largeobject_metadata WHERE oid=%s)", [loid])
            return cursor.fetchone()[0]

    @patch("knowledge.models.knowledge.is_seaweedfs_enabled", return_value=True)
    @patch("knowledge.models.knowledge.get_s3_client")
    def test_replacing_v2_files_cleans_pg_bytes_only_after_the_last_reference(self, client, _configured):
        first, last = self.create_legacy_pg_files()
        loid = first.loid
        content = b"replacement" + uuid4().bytes

        first.save(content)

        self.assertTrue(self.large_object_exists(loid))
        last.save(content)
        self.assertFalse(self.large_object_exists(loid))
        for file in (first, last):
            file.refresh_from_db()
            self.assertEqual(file.storage_type, "seaweedfs")
            self.assertIsNone(file.loid)
            self.assertEqual(file.meta["original_size"], len(content))
        client.return_value.put_object.assert_called_once()

    @patch("knowledge.models.knowledge.is_seaweedfs_enabled", return_value=True)
    @patch("knowledge.models.knowledge.get_s3_client")
    def test_replacement_rollback_restores_legacy_pg_file_and_bytes(self, _client, _configured):
        first, last = self.create_legacy_pg_files()
        loid = first.loid
        last.delete()

        with self.assertRaises(RuntimeError), transaction.atomic():
            first.save(b"replacement" + uuid4().bytes)
            self.assertFalse(self.large_object_exists(loid))
            raise RuntimeError("rollback")

        first.refresh_from_db()
        self.assertEqual((first.storage_type, first.loid), ("pg", loid))
        self.assertTrue(self.large_object_exists(loid))
