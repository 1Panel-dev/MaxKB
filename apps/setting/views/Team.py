# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： Team.py
    @date：2023/9/25 17:13
    @desc:
"""
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import PermissionConstants
from common.response import result
from setting.serializers.team_serializers import TeamMemberSerializer, get_response_body_api, \
    UpdateTeamMemberPermissionSerializer
from django.utils.translation import gettext_lazy as _


class TeamMember(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_('Get a list of team members'),
                         operation_id=_('Get a list of team members'),
                         responses=result.get_api_response(get_response_body_api()),
                         tags=[_('team')])
    @has_permissions(PermissionConstants.TEAM_READ)
    def get(self, request: Request):
        return result.success(TeamMemberSerializer(data={'team_id': str(request.user.id)}).list_member())

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_('Add member'),
                         operation_id=_('Add member'),
                         request_body=TeamMemberSerializer().get_request_body_api(),
                         tags=[_('team')])
    @has_permissions(PermissionConstants.TEAM_CREATE)
    def post(self, request: Request):
        team = TeamMemberSerializer(data={'team_id': str(request.user.id)})
        return result.success((team.add_member(**request.data)))

    class Batch(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('Add members in batches'),
                             operation_id=_('Add members in batches'),
                             request_body=TeamMemberSerializer.get_bach_request_body_api(),
                             tags=[_('team')])
        @has_permissions(PermissionConstants.TEAM_CREATE)
        def post(self, request: Request):
            return result.success(
                TeamMemberSerializer(data={'team_id': request.user.id}).batch_add_member(request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('Get team member permissions'),
                             operation_id=_('Get team member permissions'),
                             manual_parameters=TeamMemberSerializer.Operate.get_request_params_api(),
                             tags=[_('team')])
        @has_permissions(PermissionConstants.TEAM_READ)
        def get(self, request: Request, member_id: str):
            return result.success(TeamMemberSerializer.Operate(
                data={'member_id': member_id, 'team_id': str(request.user.id)}).list_member_permission())

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('Update team member permissions'),
                             operation_id=_('Update team member permissions'),
                             request_body=UpdateTeamMemberPermissionSerializer().get_request_body_api(),
                             manual_parameters=TeamMemberSerializer.Operate.get_request_params_api(),
                             tags=[_('team')]
                             )
        @has_permissions(PermissionConstants.TEAM_EDIT)
        def put(self, request: Request, member_id: str):
            return result.success(TeamMemberSerializer.Operate(
                data={'member_id': member_id, 'team_id': str(request.user.id)}).edit(request.data))

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary=_('Remove member'),
                             operation_id=_('Remove member'),
                             manual_parameters=TeamMemberSerializer.Operate.get_request_params_api(),
                             tags=[_('team')]
                             )
        @has_permissions(PermissionConstants.TEAM_DELETE)
        def delete(self, request: Request, member_id: str):
            return result.success(TeamMemberSerializer.Operate(
                data={'member_id': member_id, 'team_id': str(request.user.id)}).delete())
