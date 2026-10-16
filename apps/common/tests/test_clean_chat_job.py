from contextlib import nullcontext
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch
from uuid import UUID

from django.db.models import Q
from django.test import SimpleTestCase
from django.utils import timezone


class CleanChatPaginationTests(SimpleTestCase):
    def run_cleanup(self, count, clean_log=False):
        # Importing common.job normally starts the scheduler; keep tests isolated from background jobs.
        with patch("apscheduler.schedulers.background.BackgroundScheduler.start"):
            from common.job.clean_chat_job import clean_method

        now = timezone.now()
        chat_id = UUID(int=9999)
        records = [SimpleNamespace(id=UUID(int=i + 1), chat_id=chat_id, create_time=now) for i in range(count)]
        pages = [records[i : i + 500] for i in range(0, count, 500)]
        if count % 500 == 0:
            pages.append([])
        page_queries = []
        for page in pages:
            query = MagicMock()
            query.filter.return_value = query
            query.order_by.return_value.only.return_value.__getitem__.return_value = page
            page_queries.append(query)
        aggregate_query = MagicMock()
        aggregate_query.values.return_value.annotate.return_value = [{"chat_id": chat_id, "max_create_time": now}]
        # Cascaded delete counts can exceed the number of ChatRecords; they must not control pagination.
        aggregate_query.delete.return_value = (9999, {})
        count_query = MagicMock()
        count_query.values.return_value.annotate.return_value = [{"chat_id": chat_id, "count": 1}]
        remaining_queries = iter(page_queries)
        conditions = Q(create_time__lt=now + timedelta(days=1))

        def filter_records(*args, **kwargs):
            if args:
                self.assertEqual(args, (conditions,))
                return next(remaining_queries)
            if "chat_id__in" in kwargs:
                return count_query
            return aggregate_query

        with (
            patch("common.job.clean_chat_job.transaction.atomic", return_value=nullcontext()),
            patch("common.job.clean_chat_job.ChatRecord.objects") as manager,
            patch("common.job.clean_chat_job.Chat.objects") as chats,
            patch("common.job.clean_chat_job.File.objects") as files,
            patch("common.job.clean_chat_job.delete_orphan_chats") as delete_chats,
            patch("common.job.clean_chat_job.maxkb_logger"),
        ):
            manager.filter.side_effect = filter_records
            file = SimpleNamespace(id=UUID(int=99999))
            file_query = MagicMock()
            file_query.__iter__.return_value = [file]
            files.filter.return_value = file_query
            clean_method(conditions, clean_log=clean_log)

            self.assertEqual(sum(bool(c.args) for c in manager.filter.call_args_list), len(pages))
            for index, query in enumerate(page_queries):
                query.order_by.assert_called_once_with("id")
                if index:
                    query.filter.assert_called_once_with(id__gt=pages[index - 1][-1].id)
                else:
                    query.filter.assert_not_called()
            nonempty_pages = sum(bool(page) for page in pages)
            # One file lookup per chat per batch, rather than one per record in the chat.
            lookups = [c for c in files.filter.call_args_list if "source_id" in c.kwargs]
            self.assertEqual(len(lookups), nonempty_pages)
            self.assertTrue(all(c.kwargs["create_time__lt"] == now for c in lookups))
            deletions = [c for c in files.filter.call_args_list if "id__in" in c.kwargs]
            self.assertEqual(deletions, [call(id__in=[file.id])] * nonempty_pages)
            if not clean_log:
                aggregate_query.delete.assert_not_called()
                chats.filter.assert_not_called()
                delete_chats.assert_not_called()
            else:
                self.assertEqual(aggregate_query.delete.call_count, nonempty_pages)

    def test_files_only_processes_all_pages(self):
        self.run_cleanup(1201)

    def test_files_only_exact_batch_boundary(self):
        self.run_cleanup(500)

    def test_files_only_one_record_after_boundary(self):
        self.run_cleanup(501)

    def test_empty_queryset(self):
        self.run_cleanup(0)

    def test_log_deletion_uses_same_cursor_without_offset_skips(self):
        self.run_cleanup(1001, clean_log=True)
