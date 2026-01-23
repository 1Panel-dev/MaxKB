# coding=utf-8
"""
    @project: MaxKB
    @Author：niu
    @file： trigger.py
    @date：2026/1/14 11:48
    @desc:
"""
import os.path
import re
from typing import Dict

import uuid_utils.compat as uuid
from django.core import validators
from django.db import models, transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import Application
from common.db.search import page_search, get_dynamics_model, native_page_search, native_search
from common.exception.app_exception import AppApiException
from common.field.common import ObjectField
from common.utils.common import get_file_content
from knowledge.serializers.common import BatchSerializer
from maxkb.conf import PROJECT_DIR
from tools.models import Tool
from trigger.models import TriggerTypeChoices, Trigger, TriggerTaskTypeChoices, TriggerTask


class BatchActiveSerializer(serializers.Serializer):
    id_list = serializers.ListField(required=True, child=serializers.UUIDField(required=True), label=_('id list'))
    is_active = serializers.BooleanField(required=True, label=_("is_active"))

    def is_valid(self, *, model=None, raise_exception=False):
        super().is_valid(raise_exception=True)
        if model is not None:
            id_list = self.data.get('id_list')
            model_list = QuerySet(model).filter(id__in=id_list)
            if len(model_list) != len(id_list):
                model_id_list = [str(m.id) for m in model_list]
                error_id_list = list(filter(lambda row_id: not model_id_list.__contains__(row_id), id_list))
                raise AppApiException(500, _('The following id does not exist: {error_id_list}').format(
                    error_id_list=error_id_list))


class InputField(serializers.Serializer):
    source = serializers.CharField(required=True, label=_("source"), validators=[
        validators.RegexValidator(regex=re.compile("^custom|reference$"),
                                  message=_("The field only supports custom|reference"), code=500)
    ])
    value = ObjectField(required=True, label=_("Variable Value"), model_type_list=[str, list])


class ApplicationTaskParameterSerializer(serializers.Serializer):
    question = InputField(required=True)
    api_input_field_list = serializers.JSONField(required=False)
    user_input_field_list = serializers.JSONField(required=False)
    image_list = InputField(required=False)
    document_list = InputField(required=False)
    audio_list = InputField(required=False)
    video_list = InputField(required=False)
    other_list = InputField(required=False)

    @staticmethod
    def _validate_input_dict(value, field_name):
        if not value:
            return value
        if not isinstance(value, dict):
            raise serializers.ValidationError(f"{field_name} must be a dict")

        for key, val in value.items():
            serializer = InputField(data=val)
            if not serializer.is_valid():
                raise serializers.ValidationError({f"{field_name}.{key}": serializer.errors})
        return value

    def validate_api_input_field_list(self, value):
        return self._validate_input_dict(value, 'api_input_field_list')

    def validate_user_input_field_list(self, value):
        return self._validate_input_dict(value, 'user_input_field_list')


class ToolTaskParameterSerializer(serializers.Serializer):
    input_field_list = serializers.JSONField(required=False)

    def validate_input_field_list(self, value):
        if not value:
            return value
        if not isinstance(value, dict):
            raise serializers.ValidationError("input_field_list must be a dict")

        for key, val in value.items():
            serializer = InputField(data=val)
            if not serializer.is_valid():
                raise serializers.ValidationError({
                    key: serializer.errors
                })

        return value


class TriggerTaskCreateRequest(serializers.Serializer):
    source_type = serializers.ChoiceField(required=True, choices=TriggerTaskTypeChoices)
    source_id = serializers.CharField(required=True, label=_('source_id'))
    is_active = serializers.BooleanField(required=False, label=_('Is active'))
    meta = serializers.DictField(default=dict, required=False)
    parameter = serializers.DictField(default=dict, required=False)

    def validate(self, attrs):
        source_type = attrs.get('source_type')
        parameter = attrs.get('parameter')
        if source_type == TriggerTaskTypeChoices.APPLICATION:
            serializer = ApplicationTaskParameterSerializer(data=parameter)
            serializer.is_valid(raise_exception=True)
            attrs['parameter'] = serializer.validated_data
        if source_type == TriggerTaskTypeChoices.TOOL:
            serializer = ToolTaskParameterSerializer(data=parameter)
            serializer.is_valid(raise_exception=True)
            attrs['parameter'] = serializer.validated_data

        return attrs


class TriggerTaskEditRequest(serializers.Serializer):
    source_type = serializers.ChoiceField(required=False, choices=TriggerTaskTypeChoices)
    source_id = serializers.CharField(required=False, label=_('source_id'))
    is_active = serializers.BooleanField(required=False, label=_('Is active'))
    meta = serializers.DictField(default=dict, required=False)
    parameter = serializers.DictField(default=dict, required=False)

    def validate(self, attrs):
        source_type = attrs.get('source_type')
        parameter = attrs.get('parameter')
        if source_type == TriggerTaskTypeChoices.APPLICATION:
            serializer = ApplicationTaskParameterSerializer(data=parameter)
            serializer.is_valid(raise_exception=True)
            attrs['parameter'] = serializer.validated_data
        if source_type == TriggerTaskTypeChoices.TOOL:
            serializer = ToolTaskParameterSerializer(data=parameter)
            serializer.is_valid(raise_exception=True)
            attrs['parameter'] = serializer.validated_data

        return attrs


class TriggerEditRequest(serializers.Serializer):
    name = serializers.CharField(required=False, label=_('trigger name'))
    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('trigger description'))
    trigger_type = serializers.ChoiceField(required=False, choices=TriggerTypeChoices)
    trigger_setting = serializers.DictField(required=False, label=_("trigger setting"))
    meta = serializers.DictField(default=dict, required=False)
    is_active = serializers.BooleanField(required=False, label=_('Is active'))
    trigger_task = TriggerTaskEditRequest(many=True, required=False)


class TriggerCreateRequest(serializers.Serializer):
    id = serializers.UUIDField(required=True, label=_("Trigger ID"))
    name = serializers.CharField(required=True, label=_('trigger name'))
    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('trigger description'))
    trigger_type = serializers.ChoiceField(required=True, choices=TriggerTypeChoices)
    trigger_setting = serializers.DictField(required=True, label=_("trigger setting"))
    meta = serializers.DictField(default=dict, required=False)
    is_active = serializers.BooleanField(required=False, label=_('Is active'))
    trigger_task = TriggerTaskCreateRequest(many=True)

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        trigger_type = self.data.get('trigger_type')
        trigger_setting = self.data.get('trigger_setting', {})

        if trigger_type == TriggerTypeChoices.SCHEDULED:
            self._validate_scheduled_setting(trigger_setting)

        elif trigger_type == TriggerTypeChoices.EVENT:
            self._validate_event_setting(trigger_setting)
        else:
            raise AppApiException(500, _('Error trigger type'))

        return True

    @staticmethod
    def _validate_required_field(setting, field_name, trigger_type):
        if field_name not in setting:
            raise serializers.ValidationError({
                'trigger_setting': f'{trigger_type} type requires {field_name} field'
            })

    @staticmethod
    def _validate_non_empty_array(value, field_name):
        if not isinstance(value, list):
            raise serializers.ValidationError({
                'trigger_setting': f'{field_name} must be an array'
            })
        if len(value) == 0:
            raise serializers.ValidationError({
                'trigger_setting': f'{field_name} must not be empty'
            })

    @staticmethod
    def _validate_number_range(values, field_name, min_val, max_val):
        for val in values:
            try:
                num = int(str(val))
                if num < min_val or num > max_val:
                    raise ValueError
            except (ValueError, TypeError):
                raise serializers.ValidationError({
                    'trigger_setting': f'{field_name} values must be between "{min_val}" and "{max_val}"'
                })

    def _validate_time_array(self, time_list):
        self._validate_non_empty_array(time_list, 'time')

        for time_str in time_list:
            self._validate_time_format(time_str)

    @staticmethod
    def _validate_time_format(time_str):
        import re

        pattern = r'^([01]\d|2[0-3]):([0-5]\d)$'
        if not re.match(pattern, str(time_str)):
            raise serializers.ValidationError({
                'trigger_setting': f'Invalid time format: {time_str}, must be HH:MM (e.g., 09:00)'
            })

    def _validate_scheduled_setting(self, setting):
        schedule_type = setting.get('schedule_type')

        valid_types = ['daily', 'weekly', 'monthly', 'interval']
        if schedule_type not in valid_types:
            raise serializers.ValidationError({'trigger_setting': f'schedule_type must be one of {valid_types}'})
        if schedule_type == 'daily':
            self._validate_daily(setting)
        elif schedule_type == 'weekly':
            self._validate_weekly(setting)
        elif schedule_type == 'monthly':
            self._validate_monthly(setting)
        elif schedule_type == 'interval':
            self._validate_interval(setting)

    def _validate_daily(self, setting):
        self._validate_required_field(setting, 'time', 'daily')
        self._validate_time_array(setting['time'])

    def _validate_weekly(self, setting):
        self._validate_required_field(setting, 'days', 'weekly')
        self._validate_required_field(setting, 'time', 'weekly')
        days = setting['days']
        self._validate_non_empty_array(days, 'days')
        self._validate_number_range(days, 'days', 1, 7)
        self._validate_time_array(setting['time'])

    def _validate_monthly(self, setting):
        self._validate_required_field(setting, 'days', 'monthly')
        self._validate_required_field(setting, 'time', 'monthly')
        days = setting['days']
        self._validate_non_empty_array(days, 'days')
        self._validate_number_range(days, 'days', 1, 31)
        self._validate_time_array(setting['time'])

    def _validate_interval(self, setting):
        self._validate_required_field(setting, 'interval_value', 'interval')
        self._validate_required_field(setting, 'interval_unit', 'interval')
        interval_value = setting['interval_value']
        interval_unit = setting['interval_unit']
        try:
            value_int = int(interval_value)
            if value_int < 1:
                raise ValueError
        except (ValueError, TypeError):
            raise serializers.ValidationError({
                'trigger_setting': 'interval_value must be an integer greater than or equal to 1'
            })
        valid_units = ['minutes', 'hours']
        if interval_unit not in valid_units:
            raise serializers.ValidationError({
                'trigger_setting': f'interval_unit must be one of {valid_units}'
            })

    @staticmethod
    def _validate_event_setting(setting):
        body = setting.get('body')
        if body is not None and not isinstance(body, list):
            raise serializers.ValidationError({
                'trigger_setting': 'body must be an array'
            })


class TriggerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trigger
        fields = "__all__"


class TriggerTaskModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TriggerTask
        fields = "__all__"


class ApplicationTriggerTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['id', 'name', 'work_flow', 'icon', 'type']


class ToolTriggerTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = ['id', 'name', 'input_field_list', 'icon']


class TriggerResponse(serializers.ModelSerializer):
    class Meta:
        model = Trigger
        fields = "__all__"


class TriggerSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))
    user_id = serializers.UUIDField(required=True, label=_("User ID"))

    @transaction.atomic
    def insert(self, instance, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            TriggerCreateRequest(data=instance).is_valid(raise_exception=True)

        trigger_id = instance.get('id') if instance.get('id') else uuid.uuid7()

        trigger_model = Trigger(
            id=trigger_id,
            name=instance.get('name'),
            workspace_id=self.data.get('workspace_id'),
            desc=instance.get('desc') or '',
            trigger_type=instance.get('trigger_type'),
            trigger_setting=instance.get('trigger_setting'),
            meta=instance.get('meta', {}),
            is_active=False,
            user_id=self.data.get('user_id'),
        )
        trigger_model.save()

        trigger_tasks = instance.get('trigger_task')
        if trigger_tasks:
            trigger_task_models = [
                self.to_trigger_task_model(trigger_id, task) for task in
                trigger_tasks
            ]
            TriggerTask.objects.bulk_create(trigger_task_models)
        else:
            raise AppApiException(500, _('Trigger task can not be empty'))

        return TriggerResponse(trigger_model).data

    @staticmethod
    def to_trigger_task_model(trigger_id: str, task_data: dict):
        return TriggerTask(
            id=uuid.uuid7(),
            trigger_id=trigger_id,
            source_type=task_data.get('source_type'),
            source_id=task_data.get('source_id'),
            is_active=task_data.get('is_active', False),
            parameter=task_data.get('parameter', {}),
            meta=task_data.get('meta', {})
        )

    class Batch(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        user_id = serializers.UUIDField(required=True, label=_("User ID"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)

        @transaction.atomic
        def batch_delete(self, instance: Dict, with_valid=True):
            if with_valid:
                BatchSerializer(data=instance).is_valid(model=Trigger, raise_exception=True)
                self.is_valid(raise_exception=True)
            workspace_id = self.data.get("workspace_id")
            trigger_id_list = instance.get("id_list")

            TriggerTask.objects.filter(trigger_id__in=trigger_id_list).delete()
            Trigger.objects.filter(workspace_id=workspace_id, id__in=trigger_id_list).delete()

            return True

        def batch_switch(self, instance: Dict, with_valid=True):
            if with_valid:
                BatchActiveSerializer(data=instance).is_valid(model=Trigger, raise_exception=True)
                self.is_valid(raise_exception=True)
            workspace_id = self.data.get("workspace_id")
            trigger_id_list = instance.get("id_list")
            is_active = instance.get("is_active")
            Trigger.objects.filter(workspace_id=workspace_id, id__in=trigger_id_list, is_active=not is_active).update(
                is_active=is_active)
            return True


class TriggerOperateSerializer(serializers.Serializer):
    trigger_id = serializers.UUIDField(required=True, label=_('trigger id'))
    user_id = serializers.UUIDField(required=True, label=_("User ID"))
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        query_set = QuerySet(Trigger).filter(id=self.data.get('trigger_id'))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, _('Trigger id does not exist'))

    @transaction.atomic
    def edit(self, instance: Dict, with_valid=True):
        if with_valid:
            self.is_valid()
            TriggerEditRequest(data=instance).is_valid(raise_exception=True)
        trigger_id = self.data.get('trigger_id')
        trigger = Trigger.objects.filter(id=trigger_id).first()
        if not trigger:
            raise serializers.ValidationError(_('Trigger not found'))

        trigger_edit_field_list = ['name', 'desc', 'trigger_type', 'trigger_setting', 'meta', 'is_active']

        for field in trigger_edit_field_list:
            if field in instance:
                trigger.__setattr__(field, instance.get(field))
        trigger.save()
        # 处理trigger task
        trigger_tasks = instance.get('trigger_task')
        if trigger_tasks:
            TriggerTask.objects.filter(trigger_id=trigger_id).delete()
            trigger_task_model_list = [TriggerTask(
                id=uuid.uuid7(),
                trigger_id=trigger_id,
                source_type=task_data.get('source_type'),
                source_id=task_data.get('source_id'),
                is_active=task_data.get('is_active', False),
                parameter=task_data.get('parameter', []),
                meta=task_data.get('meta', {})
            ) for task_data in trigger_tasks]
            TriggerTask.objects.bulk_create(trigger_task_model_list)

        return self.one(with_valid=False)

    def delete(self):
        self.is_valid(raise_exception=True)
        trigger_id = self.data.get('trigger_id')
        TriggerTask.objects.filter(trigger_id=trigger_id).delete()
        Trigger.objects.filter(id=trigger_id).delete()
        return True

    def one(self, with_valid=True):
        if with_valid:
            self.is_valid()
        trigger_id = self.data.get('trigger_id')
        workspace_id = self.data.get('workspace_id')
        trigger = QuerySet(Trigger).filter(workspace_id=workspace_id, id=trigger_id).first()

        trigger_tasks = list(QuerySet(TriggerTask).filter(trigger_id=trigger_id))

        application_ids = []
        tool_ids = []
        for task in trigger_tasks:
            if task.source_type == TriggerTaskTypeChoices.APPLICATION:
                application_ids.append(task.source_id)
            elif task.source_type == TriggerTaskTypeChoices.TOOL:
                tool_ids.append(task.source_id)

        trigger_task_list = TriggerTaskModelSerializer(trigger_tasks, many=True).data

        application_task_list = []
        if application_ids:
            applications =Application.objects.filter(workspace_id=workspace_id, id__in=application_ids)
            application_task_list = ApplicationTriggerTaskSerializer(applications, many=True).data
        tool_task_list = []
        if tool_ids:
            tools = Tool.objects.filter(workspace_id=workspace_id, id__in=tool_ids)
            tool_task_list = ToolTriggerTaskSerializer(tools, many=True).data

        return {
            **TriggerModelSerializer(trigger).data,
            'trigger_task': trigger_task_list,
            'application_task_list': application_task_list,
            'tool_task_list': tool_task_list,
        }


class TriggerQuerySerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('Trigger name'))
    type = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_('Trigger type'))
    is_active = serializers.BooleanField(required=False, allow_null=True, label=_('Is active'))
    task = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_('Trigger task'))
    create_user = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_('Create user'))
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))

    def get_query_set(self):
        trigger_query_set = QuerySet(
            model=get_dynamics_model({
                'name': models.CharField(),
                'trigger_type': models.CharField(),
                't.workspace_id': models.CharField(),
                't.is_active': models.BooleanField(),
                't.user_id': models.CharField(),
            }))
        task_query_set = QuerySet(model=get_dynamics_model({
            'trigger_task_str': models.CharField(),
        }))
        trigger_query_set = trigger_query_set.filter(**{'t.workspace_id': self.data.get("workspace_id")})
        if self.data.get("name"):
            trigger_query_set = trigger_query_set.filter(name__contains=self.data.get("name"))
        if self.data.get("type"):
            trigger_query_set = trigger_query_set.filter(trigger_type=self.data.get("type"))
        if self.data.get("is_active") is not None:
            trigger_query_set = trigger_query_set.filter(**{"t.is_active": self.data.get("is_active")})
        if self.data.get("task"):
            task_query_set = task_query_set.filter(trigger_task_str__icontains=self.data.get("task"))
        if self.data.get("create_user"):
            trigger_query_set = trigger_query_set.filter(**{"t.user_id": self.data.get("create_user")})

        return {"trigger_query_set": trigger_query_set, "task_query_set": task_query_set}

    def page(self, current_page: int, page_size: int, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        return native_page_search(current_page, page_size, self.get_query_set(), get_file_content(
            os.path.join(PROJECT_DIR, "apps", "trigger", "sql", "get_trigger_page_list.sql")
        ))

    def list(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        return native_search(self.get_query_set(), select_string=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "trigger", "sql", "get_trigger_page_list.sql")))
