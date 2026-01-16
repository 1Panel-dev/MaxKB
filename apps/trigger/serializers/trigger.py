# coding=utf-8
"""
    @project: MaxKB
    @Author：niu
    @file： trigger.py
    @date：2026/1/14 11:48
    @desc:
"""
import re
from typing import Dict

import uuid_utils.compat as uuid
from django.core import validators
from django.db import models, transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import Application
from common.db.search import page_search
from common.exception.app_exception import AppApiException
from common.field.common import ObjectField
from tools.models import Tool
from trigger.models import TriggerTypeChoices, Trigger, TriggerTaskTypeChoices, TriggerTask


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

    def validate_input_field_list(self,value):
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


class TriggerCreateRequest(serializers.Serializer):
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
        self._validate_required_field(setting, 'weekdays', 'weekly')
        self._validate_required_field(setting, 'time', 'weekly')
        weekdays = setting['weekdays']
        self._validate_non_empty_array(weekdays, 'weekdays')
        self._validate_number_range(weekdays, 'weekdays', 1, 7)
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

        trigger_id = uuid.uuid7()

        trigger_model = Trigger(
            id=trigger_id,
            name=instance.get('name'),
            workspace_id=self.data.get('workspace_id'),
            desc=instance.get('desc'),
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
            TriggerCreateRequest(data=instance).is_valid(raise_exception=True)
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
        TriggerTask.objects.filter(trigger_id=trigger_id).delete()
        trigger_tasks = instance.get('trigger_task')
        if trigger_tasks:
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
        else:
            raise AppApiException(500, _('Trigger task can not be empty'))
        return self.one(with_valid=False)

    def delete(self):
        self.is_valid(raise_exception=True)
        trigger_id = self.data.get('trigger_id')
        Trigger.objects.filter(id=trigger_id).delete()
        return True

    def one(self, with_valid=True):
        if with_valid:
            self.is_valid()
        trigger_id = self.data.get('trigger_id')
        trigger = QuerySet(Trigger).filter(id=trigger_id).first()

        trigger_tasks = QuerySet(TriggerTask).filter(trigger_id=trigger_id)
        application_ids = [str(task.source_id) for task in trigger_tasks if
                           task.source_type == TriggerTaskTypeChoices.APPLICATION]
        tool_ids = [str(task.source_id) for task in trigger_tasks if task.source_type == TriggerTaskTypeChoices.TOOL]

        application_task_list = [ApplicationTriggerTaskSerializer(application).data for application in
                                 QuerySet(Application).filter(id__in=application_ids)]

        tool_task_list = [ToolTriggerTaskSerializer(tool).data for tool in QuerySet(Tool).filter(id__in=tool_ids)]

        return {
            **TriggerModelSerializer(trigger).data,
            'application_task_list': application_task_list,
            'tool_task_list': tool_task_list,
        }


class TriggerQuerySerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('Trigger name'))
    type = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_('Trigger type'))
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))

    def get_query_set(self):
        query_set = QuerySet(Trigger).filter(workspace_id=self.data.get("workspace_id"))
        if self.data.get("name"):
            query_set = query_set.filter(name__contains=self.data.get('name'))
        if self.data.get('type'):
            query_set = query_set.filter(trigger_type=self.data.get('type'))
        return query_set

    def page(self, current_page: int, page_size: int, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        return page_search(current_page, page_size, self.get_query_set(), lambda row: TriggerResponse(row).data)

    def list(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        return [TriggerResponse(row).data for row in self.get_query_set()]
