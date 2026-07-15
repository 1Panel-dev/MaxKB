# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： form_node.py
    @date：2026/7/6 15:30
    @desc:
"""
import copy
import re

import uuid_utils.compat as uuid
from rest_framework import serializers

from django.utils.translation import gettext_lazy as _

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode, Signal
from application.workflow.message.struct.content import NodeInfo, Position
from application.workflow.message.struct.form_content import FormContent
from application.workflow.status import Status

_TEMPLATE_RE = re.compile(r'\{\{([^.\s}]+)\.([^.\s}]+)\}\}')

_MULTI_SELECT_TYPES = {'MultiSelect', 'MultiRow'}


def _get_default_option(option_list, _type, value_field):
    try:
        if option_list and isinstance(option_list, list) and len(option_list) > 0:
            default_value_list = [o.get(value_field) for o in option_list if o.get('default')]
            if len(default_value_list) == 0:
                return [option_list[0].get(value_field)] if _type in _MULTI_SELECT_TYPES else option_list[0].get(
                    value_field)
            else:
                return default_value_list if _type in _MULTI_SELECT_TYPES else default_value_list[0]
    except Exception:
        pass
    return []


class FormNodeSerializer(serializers.Serializer):
    form_field_list = serializers.ListField(required=True, label=_("Form Configuration"))
    form_content_format = serializers.CharField(required=True, label=_('Form output content'))
    form_data = serializers.DictField(required=False, allow_null=True, label=_("Form Data"))
    is_result = serializers.BooleanField(required=False, label=_('Whether to return content'))


class FormNode(INode):
    serializer_class = FormNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = 'form-node'

    def execute(self):
        node_params = self.get_parameters()
        workflow_params = self.workflow_manage.get_parameters()
        
        # 判断是否是表单提交
        position = workflow_params.get('position') or {}
        is_form_submit = position.get('id') == self.node.id
        
        form_field_list = node_params.get('form_field_list', [])
        form_content_format = node_params.get('form_content_format', '')
        
        if is_form_submit:
            # 表单提交：从 workflow_params 获取前端提交的 form_data
            form_data = workflow_params.get('form_data') or {}
            is_submit = True
            # 复用前端传来的 chunk_id
            chunk_id = workflow_params.get('chunk_id') or str(uuid.uuid7())
        else:
            # 首次执行：从节点参数获取
            form_data = node_params.get('form_data')
            is_submit = form_data is not None
            # 生成新 chunk_id
            chunk_id = str(uuid.uuid7())
        
        # 写入 context
        self.write_context('is_submit', is_submit)
        self.write_context('form_content_format', form_content_format)

        if is_submit:
            self.write_context('form_data', form_data)
            for key in form_data:
                self.write_context(key, form_data.get(key))

        form_field_list = [self._reset_field(field) for field in form_field_list]
        self.write_context('form_field_list', form_field_list)

        # 输出表单内容
        node_info = NodeInfo(self.get_node_id(), self.get_node_name(), Status.SUCCESS)
        self.write(FormContent(
            chunk_id, form_field_list, form_content_format,
            is_submit, Status.SUCCESS, node_info, Position(self.get_node_id()),
            form_data=form_data,
        ))

        # 如果未提交，中断工作流等待用户提交
        if not is_submit:
            self.complete(Status.SUCCESS, signal=Signal.FORM)
            return
        
        # 已提交，继续执行后续节点
        self.complete(Status.SUCCESS)

    def _generate_prompt(self, prompt):
        try:
            return self.workflow_manage.generate_prompt(prompt)
        except Exception:
            return prompt

    def _reset_field(self, field):
        field = copy.copy(field)
        for f in ['field', 'label', 'default_value']:
            _value = field.get(f)
            if _value is None:
                continue
            if isinstance(_value, str):
                field[f] = self._generate_prompt(_value)
            elif f == 'label' and isinstance(_value, dict):
                _label_value = _value.get('label')
                _value['label'] = self._generate_prompt(_label_value)
                tooltip = _value.get('attrs', {}).get('tooltip')
                if tooltip is not None:
                    _value['attrs']['tooltip'] = self._generate_prompt(tooltip)

        input_type = field.get('input_type')
        if input_type in {'SingleSelect', 'MultiSelect', 'RadioCard', 'RadioRow', 'MultiRow'}:
            if field.get('assignment_method') == 'ref_variables':
                option_list_ref = field.get('option_list')
                if option_list_ref and len(option_list_ref) >= 2:
                    option_list = self.workflow_manage.get_reference_field(
                        option_list_ref[0], option_list_ref[1:])
                    option_list = option_list if isinstance(option_list, list) else []
                    field['option_list'] = option_list
                    field['default_value'] = _get_default_option(
                        option_list, input_type, field.get('value_field'))

        if input_type == 'JsonInput':
            if field.get('default_value_assignment_method') == 'ref_variables':
                default_ref = field.get('default_value')
                if default_ref and isinstance(default_ref, list) and len(default_ref) >= 2:
                    field['default_value'] = self.workflow_manage.get_reference_field(
                        default_ref[0], default_ref[1:])

        self._reset_visibility_rules(field)
        return field

    def _reset_visibility_rules(self, field):
        visibility_rules = field.get('visibility_rules')
        if not visibility_rules or not isinstance(visibility_rules.get('conditions'), list):
            return
        for cond in visibility_rules['conditions']:
            cond_field = cond.get('field')
            if not cond_field or len(cond_field) < 2 or not cond_field[0] or not cond_field[1]:
                continue
            if cond_field[0] != self.node.id:
                cond['_left'] = self.workflow_manage.get_reference_field(cond_field[0], cond_field[1:])
            cond_value = cond.get("value")
            if isinstance(cond_value, str) and _TEMPLATE_RE.search(cond_value):
                cond['value'] = self._render_cond_value(cond_value)

    def _render_cond_value(self, value):
        def replacer(match):
            node_display = match.group(1)
            field_name = match.group(2)
            workflow = self.workflow_manage.workflow
            for f in workflow.node_field_list:
                if f.node_name == node_display and f.value == field_name:
                    if f.node_id == self.node.id:
                        return match.group(0)
                    ref = self.workflow_manage.get_reference_field(f.node_id, [field_name])
                    return str(ref) if ref is not None else ''
            return match.group(0)

        try:
            return _TEMPLATE_RE.sub(replacer, value)
        except Exception:
            return value
