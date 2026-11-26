from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from common.auth.constants.role_constants import RoleConstants
from common.auth.struct.auth import Auth
from common.constants.authentication_type import UserType
from common.constants.resource_permission_constants import AuthTargetType, ResourceAuthType, ResourcePermissionConstants
from common.database_model_manage.database_model_manage import DatabaseModelManage
from models_provider.models import Model
from system_manage.models import WorkspaceUserResourcePermission
from users.models import User


class WorkspaceModelListTests(TestCase):
    def test_shared_model_list_after_creator_deletion(self):
        workspace_id = "shared-model-list"
        reader = User.objects.create(username="reader", nick_name="Reader", role="USER")
        creator = User.objects.create(username="former-creator")
        shared = Model.objects.create(workspace_id="None", name="Shared", user=creator)
        owned = Model.objects.create(workspace_id="None", name="Owned", user=reader)
        Model.objects.create(workspace_id="None", name="Unshared")
        creator.delete()

        def authorized_models(queryset, requested_workspace):
            self.assertEqual(requested_workspace, workspace_id)
            return queryset.filter(id__in=[shared.id, owned.id])

        client = APIClient()
        reader.type = str(UserType.SYSTEM_USER)
        role = RoleConstants.USER.get_workspace_role()(None, {"workspace_id": workspace_id})
        client.force_authenticate(user=reader, token=Auth(roles={str(role)}, permissions={}))
        with patch.dict(DatabaseModelManage.model_dict, {"get_authorized_model": authorized_models}):
            response = client.get(f"/admin/api/system/shared/workspace/{workspace_id}/model")

        self.assertEqual(response.status_code, 200)
        rows = {row["id"]: row for row in response.json()["data"]}
        self.assertEqual(set(rows), {str(shared.id), str(owned.id)})
        self.assertIsNone(rows[str(shared.id)]["user_id"])
        self.assertEqual(rows[str(shared.id)]["username"], "")
        self.assertEqual(rows[str(shared.id)]["nick_name"], "")
        self.assertEqual(rows[str(owned.id)]["username"], reader.username)
        self.assertEqual(rows[str(owned.id)]["nick_name"], reader.nick_name)

    def test_embedding_options_include_shared_models_after_creator_deletion(self):
        workspace_id = "embedding-options"
        user = User.objects.create(username="reader", nick_name="Reader", role="USER")
        creator = User.objects.create(username="former-creator")
        local = Model.objects.create(workspace_id=workspace_id, name="Local", model_type="EMBEDDING", user=user)
        WorkspaceUserResourcePermission.objects.create(
            workspace_id=workspace_id,
            user=user,
            auth_target_type=AuthTargetType.MODEL,
            target=str(local.id),
            auth_type=ResourceAuthType.RESOURCE_PERMISSION_GROUP,
            permission_list=[ResourcePermissionConstants.VIEW],
        )
        shared = Model.objects.create(workspace_id="None", name="Shared", model_type="EMBEDDING", user=creator)
        owned = Model.objects.create(workspace_id="None", name="Owned", model_type="EMBEDDING", user=user)
        llm = Model.objects.create(workspace_id="None", name="Chat", model_type="LLM", user=user)
        Model.objects.create(workspace_id="None", name="Unshared", model_type="EMBEDDING")
        creator.delete()

        def authorized_models(queryset, requested_workspace):
            self.assertEqual(requested_workspace, workspace_id)
            return queryset.filter(id__in=[shared.id, owned.id, llm.id])

        client = APIClient()
        user.type = str(UserType.SYSTEM_USER)
        role = RoleConstants.USER.get_workspace_role()(None, {"workspace_id": workspace_id})
        client.force_authenticate(user=user, token=Auth(roles={str(role)}, permissions={}))
        with patch.dict(DatabaseModelManage.model_dict, {"get_authorized_model": authorized_models}):
            response = client.get(f"/admin/api/workspace/{workspace_id}/model_list", {"model_type": "EMBEDDING"})

        self.assertEqual(response.status_code, 200)
        groups = response.json()["data"]
        self.assertEqual([row["id"] for row in groups["model"]], [str(local.id)])
        options = {row["id"]: row for row in groups["shared_model"]}
        self.assertEqual(set(options), {str(shared.id), str(owned.id)})
        self.assertIsNone(options[str(shared.id)]["user_id"])
        self.assertEqual(options[str(shared.id)]["username"], "")
        self.assertEqual(options[str(shared.id)]["nick_name"], "")
        self.assertEqual(options[str(owned.id)]["username"], user.username)
        self.assertEqual(options[str(owned.id)]["nick_name"], user.nick_name)
