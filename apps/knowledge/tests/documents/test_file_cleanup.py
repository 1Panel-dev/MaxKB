from unittest.mock import patch
from uuid import uuid4

from django.db import transaction
from django.test import SimpleTestCase, TestCase
from knowledge.models import File
from knowledge.models.knowledge import on_delete_file
from knowledge.services.file_cleanup import delete_file_object, object_is_referenced


class FileCleanupTests(SimpleTestCase):
    def test_pg_unlinks_only_after_last_reference_and_uses_database_alias(self):
        for shared in (False, True):
            with self.subTest(shared=shared):
                with (
                    patch("knowledge.models.knowledge.File.objects") as files,
                    patch("knowledge.models.knowledge.connections") as connections,
                ):
                    files.using.return_value.filter.return_value.exists.return_value = shared
                    on_delete_file(File, File(storage_type="pg", loid=42), using="archive")
                    files.using.assert_called_once_with("archive")
                    cursor = connections.__getitem__.return_value.cursor.return_value.__enter__.return_value
                    if shared:
                        cursor.execute.assert_not_called()
                    else:
                        cursor.execute.assert_called_once_with(
                            "SELECT lo_unlink(oid) FROM pg_largeobject_metadata WHERE oid = %s", [42]
                        )

    def test_pg_without_large_object_does_nothing(self):
        with patch("knowledge.models.knowledge.connections") as connections:
            on_delete_file(File, File(storage_type="pg", loid=None), using="default")
            connections.__getitem__.assert_not_called()

    def test_oss_deletion_runs_only_after_commit(self):
        with (
            patch("knowledge.models.knowledge.transaction.on_commit") as on_commit,
            patch("knowledge.services.file_cleanup.delete_file_object") as delete,
            patch("knowledge.models.knowledge.get_bucket", return_value="bucket"),
        ):
            file = File(storage_type="seaweedfs", meta={"seaweedfs_key": "shared"})
            on_delete_file(File, file, using="archive")
            delete.assert_not_called()
            on_commit.call_args.args[0]()
            delete.assert_called_once_with("bucket", "shared", file.id, "archive")
            self.assertTrue(on_commit.call_args.kwargs["robust"])

    def test_shared_key_and_legacy_key_reference_lookup(self):
        with patch("knowledge.services.file_cleanup.File.objects") as files:
            files.using.return_value.filter.return_value.exists.return_value = True
            self.assertTrue(object_is_referenced(f"files/{uuid4()}", "archive"))
            files.using.assert_called_once_with("archive")
            condition = files.using.return_value.filter.call_args.args[0]
            self.assertIn("seaweedfs_key", str(condition))
            self.assertIn("has_key", str(condition))
            self.assertEqual(files.using.return_value.filter.call_args.kwargs, {"storage_type": "seaweedfs"})

    def test_cleanup_failure_is_logged_without_raising(self):
        with (
            patch("knowledge.services.file_cleanup.object_is_referenced", return_value=False),
            patch("knowledge.services.file_cleanup.get_s3_client", side_effect=RuntimeError("private details")),
            patch("knowledge.services.file_cleanup.maxkb_logger") as logger,
        ):
            delete_file_object("bucket", "key", "file-id")
            logger.warning.assert_called_once()
            self.assertEqual(logger.warning.call_args.args[1:], ("file-id", "RuntimeError"))


class FileCleanupDatabaseTests(TestCase):
    def setUp(self):
        self.client_patch = patch("knowledge.services.file_cleanup.get_s3_client")
        self.client = self.client_patch.start().return_value
        self.addCleanup(self.client_patch.stop)
        self.bucket_patch = patch("knowledge.models.knowledge.get_bucket", return_value="bucket")
        self.bucket_patch.start()
        self.addCleanup(self.bucket_patch.stop)

    def create_files(self):
        files = [
            File(storage_type="seaweedfs", sha256_hash="same", meta={"seaweedfs_key": "shared"}),
            File(storage_type="seaweedfs", sha256_hash="same", meta={"seaweedfs_key": "shared"}),
        ]
        File.objects.bulk_create(files)
        return files

    def test_bulk_delete_shared_object_after_commit(self):
        files = self.create_files()
        with self.captureOnCommitCallbacks(execute=True):
            File.objects.filter(pk__in=[file.pk for file in files]).delete()
            self.client.delete_object.assert_not_called()
        self.assertTrue(self.client.delete_object.called)
        for call in self.client.delete_object.call_args_list:
            self.assertEqual(call.kwargs, {"Bucket": "bucket", "Key": "shared"})

    def test_single_reference_then_last_reference(self):
        first, last = self.create_files()
        with self.captureOnCommitCallbacks(execute=True):
            first.delete()
        self.client.delete_object.assert_not_called()
        with self.captureOnCommitCallbacks(execute=True):
            last.delete()
        self.client.delete_object.assert_called_once()

    def test_rollback_restores_files_and_discards_callback(self):
        files = self.create_files()
        with self.captureOnCommitCallbacks(execute=True):
            try:
                with transaction.atomic():
                    File.objects.filter(pk__in=[file.pk for file in files]).delete()
                    raise RuntimeError("rollback")
            except RuntimeError:
                pass
        self.assertEqual(File.objects.count(), 2)
        self.client.delete_object.assert_not_called()

    def test_oss_failure_does_not_undo_file_deletion(self):
        files = self.create_files()
        self.client.delete_object.side_effect = RuntimeError("offline")
        with patch("knowledge.services.file_cleanup.maxkb_logger") as logger:
            with self.captureOnCommitCallbacks(execute=True):
                File.objects.filter(pk__in=[file.pk for file in files]).delete()
            self.assertTrue(logger.warning.called)
        self.assertFalse(File.objects.exists())

    def test_same_hash_different_object_does_not_prevent_deletion(self):
        first, last = self.create_files()
        File.objects.filter(pk=last.pk).update(meta={"seaweedfs_key": "different"})
        with self.captureOnCommitCallbacks(execute=True):
            first.delete()
        self.client.delete_object.assert_called_once_with(Bucket="bucket", Key="shared")
        self.assertTrue(File.objects.filter(pk=last.pk).exists())
