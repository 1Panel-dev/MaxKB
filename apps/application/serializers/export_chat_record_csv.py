# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： export_chat_record_csv.py
    @date：2025/7/14 11:00
    @desc: CSV export for conversation logs, aggregated by chat
"""
import csv
import io
import re
import urllib.parse
from datetime import datetime

import pytz
from django.db.models import Prefetch
from django.http import StreamingHttpResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import Chat, ChatRecord, Application
from common.exception.app_exception import AppApiException
from maxkb.settings import TIME_ZONE

ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010\013\014\016-\037]')


class ApplicationChatExportCsvSerializer(serializers.Serializer):
    start_time = serializers.DateField(format='%Y-%m-%d', label=_('Start time'))
    end_time = serializers.DateField(format='%Y-%m-%d', label=_('End time'))
    fields = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        label=_('Export fields')
    )
    application_id = serializers.UUIDField(required=True, label=_('Application ID'))

    ALL_FIELDS = {
        'session_id': _('Session ID'),
        'user_id': _('User ID'),
        'user_name': _('User Name'),
        'chat_time': _('Chat Time'),
        'user_question': _('User Question'),
        'ai_answer': _('AI Answer'),
        'chat_round': _('Chat Rounds'),
        'input_tokens': _('Input Tokens'),
        'output_tokens': _('Output Tokens'),
        'total_tokens': _('Total Tokens'),
        'cost': _('Cost'),
        'model_name': _('Model Name'),
        'knowledge_calls': _('Knowledge Base Calls'),
        'response_time': _('Response Time (s)'),
        'error_code': _('Error Code'),
    }

    def validate_fields(self, value):
        valid_fields = set(self.ALL_FIELDS.keys())
        for f in value:
            if f not in valid_fields:
                raise AppApiException(500, _('Invalid field: {}').format(f))
        if not value:
            raise AppApiException(500, _('At least one field must be selected'))
        return value

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        app = Application.objects.filter(id=self.validated_data['application_id']).first()
        if not app:
            raise AppApiException(500, _('Application does not exist'))

        start = self.validated_data['start_time']
        end = self.validated_data['end_time']
        now = timezone.now().date()

        if end > now:
            raise AppApiException(500, _('End time cannot be later than current time'))

        app_created = app.create_time.date() if timezone.is_aware(app.create_time) else app.create_time.date()
        if start < app_created:
            raise AppApiException(500, _('Start time cannot be earlier than application creation time'))

        if (end - start).days > 90:
            raise AppApiException(500, _('Maximum export range is 90 days, please narrow the time range'))

        return True

    def get_start_datetime(self):
        d = self.validated_data['start_time']
        naive = datetime.combine(d, datetime.min.time())
        return timezone.make_aware(naive, timezone.get_default_timezone())

    def get_end_datetime(self):
        d = self.validated_data['end_time']
        naive = datetime.combine(d, datetime.max.time())
        return timezone.make_aware(naive, timezone.get_default_timezone())

    @staticmethod
    def extract_model_name(records):
        for record in records:
            details = record.details or {}
            for key, node in details.items():
                if isinstance(node, dict):
                    m = node.get('model_name')
                    if m:
                        return m
                    if node.get('type') in ('ai-chat-node', 'question-node'):
                        if node.get('model_id'):
                            return node.get('model_id', '')
        return ''

    @staticmethod
    def extract_knowledge_calls(records):
        knowledge_count = 0
        for record in records:
            details = record.details or {}
            for key, node in details.items():
                if isinstance(node, dict):
                    if node.get('type') == 'search-knowledge-node':
                        knowledge_count += len(node.get('paragraph_list') or [])
                    elif node.get('step_type') == 'search_step':
                        knowledge_count += len(node.get('paragraph_list') or [])
                    elif node.get('type') == 'reranker-node':
                        knowledge_count += len(node.get('result_list') or [])
            search_step = details.get('search_step')
            if search_step:
                knowledge_count += len(search_step.get('paragraph_list') or [])
        return str(knowledge_count)

    @staticmethod
    def extract_error_code(records):
        for record in records:
            details = record.details or {}
            for key, node in details.items():
                if isinstance(node, dict):
                    status = node.get('status')
                    if status and status != 200:
                        return str(status)
                    if node.get('err_message'):
                        return 'ERROR'
        return ''

    @staticmethod
    def safe_csv_value(value, max_length=32767):
        if value is None:
            return ''
        if not isinstance(value, str):
            value = str(value)
        value = ILLEGAL_CHARACTERS_RE.sub('', value)
        if len(value) > max_length:
            value = value[:max_length] + '...(truncated)'
        if ',' in value or '"' in value or '\n' in value or '\r' in value:
            value = value.replace('"', '""')
            value = '"' + value + '"'
        return value

    def chat_to_row(self, chat, selected_fields):
        records = getattr(chat, 'records', [])
        total_message_tokens = sum(r.message_tokens or 0 for r in records)
        total_answer_tokens = sum(r.answer_tokens or 0 for r in records)
        total_cost = sum(r.const or 0 for r in records)
        total_run_time = sum(r.run_time or 0 for r in records)

        first_record = records[0] if records else None
        last_record = records[-1] if records else None

        create_time_str = ''
        if chat.create_time:
            tz_time = chat.create_time.astimezone(pytz.timezone(TIME_ZONE))
            create_time_str = tz_time.strftime('%Y-%m-%d %H:%M:%S')

        field_map = {
            'session_id': str(chat.id),
            'user_id': str(chat.chat_user_id or ''),
            'user_name': (chat.asker or {}).get('username', ''),
            'chat_time': create_time_str,
            'user_question': first_record.problem_text if first_record else '',
            'ai_answer': last_record.answer_text if last_record else '',
            'chat_round': str(chat.chat_record_count),
            'input_tokens': str(total_message_tokens),
            'output_tokens': str(total_answer_tokens),
            'total_tokens': str(total_message_tokens + total_answer_tokens),
            'cost': str(total_cost),
            'model_name': self.extract_model_name(records),
            'knowledge_calls': self.extract_knowledge_calls(records),
            'response_time': str(round(total_run_time, 2)),
            'error_code': self.extract_error_code(records),
        }
        return [self.safe_csv_value(field_map.get(f, '')) for f in selected_fields]

    def export(self):
        selected_fields = self.validated_data['fields']
        headers = [str(self.ALL_FIELDS[f]) for f in selected_fields]

        app = Application.objects.get(id=self.validated_data['application_id'])
        filename = "{}_{}_{}_{}.csv".format(
            app.name, _('Chat Log'),
            self.validated_data['start_time'], self.validated_data['end_time']
        )

        def stream():
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            yield '\ufeff'
            writer.writerow(headers)
            yield buffer.getvalue()
            buffer.seek(0)
            buffer.truncate(0)

            start_dt = self.get_start_datetime()
            end_dt = self.get_end_datetime()

            chat_ids = list(Chat.objects.filter(
                application_id=self.validated_data['application_id'],
                create_time__gte=start_dt,
                create_time__lte=end_dt,
                is_deleted=False,
            ).values_list('id', flat=True).order_by('-create_time'))

            batch_size = 200
            total = len(chat_ids)

            for i in range(0, total, batch_size):
                batch_ids = chat_ids[i:i + batch_size]
                chats = Chat.objects.filter(id__in=batch_ids).prefetch_related(
                    Prefetch('chatrecord_set',
                             queryset=ChatRecord.objects.all().order_by('index'),
                             to_attr='records')
                ).order_by('-create_time')

                for chat in chats:
                    writer.writerow(self.chat_to_row(chat, selected_fields))

                yield buffer.getvalue()
                buffer.seek(0)
                buffer.truncate(0)

            buffer.close()

        response = StreamingHttpResponse(
            stream(),
            content_type='text/csv; charset=utf-8'
        )
        encoded_name = urllib.parse.quote(filename)
        response['Content-Disposition'] = "attachment; filename*=UTF-8''{}".format(encoded_name)
        return response
