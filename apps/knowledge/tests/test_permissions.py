import json
from types import SimpleNamespace
from unittest.mock import patch

from django.http import QueryDict
from django.test import SimpleTestCase

from common.auth.constants.group_constants import Group
from common.auth.constants.permission_constants import PermissionConstants as P, RESOURCE_PERMISSION_MAP
from common.auth.handle.impl.user_token import get_permissions
from common.auth.struct.aggregate_permission import AggregatePermission
from common.constants.resource_permission_constants import ResourceAuthType
from common.exception.app_exception import AppUnauthorizedFailed
from knowledge.permissions import knowledge_permission
from knowledge.views.document import DocumentView
from knowledge.views.external_service import ExternalServiceView, KnowledgeMcpConfigView
from knowledge.views.image_document import ImageDocumentView
from knowledge.views.knowledge import KnowledgeView


class WorkspaceKnowledgePermissionTests(SimpleTestCase):
    workspace_id = "workspace-a"
    knowledge_id = "00000000-0000-0000-0000-000000000001"
    document_id = "00000000-0000-0000-0000-000000000002"

    def request(self, *permissions, data=None, query=None, roles=()):
        bitmap = {}
        for permission in permissions:
            value = permission.get_workspace_knowledge_permission()(None, self.kwargs())
            key = value.get_resource_permission_key(None)
            bitmap[key] = bitmap.get(key, 0) | value.bit()
        params = QueryDict(mutable=True)
        params.update(query or {})
        return SimpleNamespace(
            auth=SimpleNamespace(roles=roles, permissions=bitmap),
            user=SimpleNamespace(id=self.document_id, type="test"),
            META={},
            path="/test",
            data=data or {},
            query_params=params,
        )

    def kwargs(self):
        return {"workspace_id": self.workspace_id, "knowledge_id": self.knowledge_id}

    def test_all_workspace_knowledge_bits_are_independent_and_scoped(self):
        permissions = [p for p in P if p.value.group == Group.KNOWLEDGE]
        for granted in permissions:
            request = self.request(granted)
            for required in permissions:
                permission = required.get_workspace_knowledge_permission()
                with self.subTest(granted=granted.name, required=required.name):
                    self.assertEqual(
                        AggregatePermission(permissions=[permission]).hasPermission(request, **self.kwargs()),
                        granted == required,
                    )
            self.assertFalse(
                knowledge_permission(granted).hasPermission(
                    request, workspace_id="workspace-b", knowledge_id=self.knowledge_id
                )
            )
            self.assertFalse(
                knowledge_permission(granted).hasPermission(
                    request, workspace_id=self.workspace_id, knowledge_id=self.document_id
                )
            )

    def test_administrators_and_explicit_owner_keep_access(self):
        for request in [
            self.request(roles=["ADMIN"]),
            self.request(roles=[f"WORKSPACE_MANAGE:w:{self.workspace_id}"]),
            self.request(P.KNOWLEDGE, roles=[f"USER:w:{self.workspace_id}"]),
        ]:
            self.assertTrue(knowledge_permission(P.KNOWLEDGE_IMAGE_VECTOR).hasPermission(request, **self.kwargs()))
        request = self.request(P.KNOWLEDGE_DOCUMENT_READ, roles=[f"USER:w:{self.workspace_id}"])
        self.assertFalse(knowledge_permission(P.KNOWLEDGE_IMAGE_VECTOR).hasPermission(request, **self.kwargs()))

    def test_new_permissions_appear_in_workspace_role_tree(self):
        from role_setting.serializers.role_setting_serializers import _build_permission_tree, UserGroup

        tree = _build_permission_tree(UserGroup, "USER")
        knowledge = next(group for group in tree if group["id"] == "KNOWLEDGE")
        children = {child["id"]: child for child in knowledge["children"]}
        for group, count in [
            ("IMAGE", 11),
            ("SCHEDULED_SYNC", 2),
            ("DOCUMENT_STRATEGY", 2),
            ("EXTERNAL_SERVICE", 2),
            ("KNOWLEDGE_SETTING", 2),
        ]:
            self.assertEqual(len(children[group]["permission"]), count)
        ids = {p["id"] for p in children["KNOWLEDGE"]["permission"]}
        self.assertIn(str(P.KNOWLEDGE_MCP_CONFIG.value), ids)
        self.assertIn(str(P.KNOWLEDGE_EXPORT_SKILLS.value), ids)

    @patch("knowledge.views.document.DocumentSerializers.Query")
    def test_image_and_document_lists_require_their_own_read_permission(self, serializer):
        serializer.return_value.list.return_value = []
        for permission, resource_type in [(P.KNOWLEDGE_IMAGE_READ, "image"), (P.KNOWLEDGE_DOCUMENT_READ, "document")]:
            DocumentView().get(self.request(permission, query={"resource_type": resource_type}), **self.kwargs())
            with self.assertRaises(AppUnauthorizedFailed):
                DocumentView().get(
                    self.request(
                        permission, query={"resource_type": "document" if resource_type == "image" else "image"}
                    ),
                    **self.kwargs(),
                )

    @patch("knowledge.views.image_document.ImageDocumentSerializers.Preview")
    def test_document_create_cannot_upload_images(self, serializer):
        serializer.return_value.upload.return_value = []
        ImageDocumentView.Preview().post(self.request(P.KNOWLEDGE_IMAGE_CREATE), **self.kwargs())
        with self.assertRaises(AppUnauthorizedFailed):
            ImageDocumentView.Preview().post(self.request(P.KNOWLEDGE_DOCUMENT_CREATE), **self.kwargs())

    @patch("common.log.log.Log")
    @patch("knowledge.views.document.DocumentSerializers.Operate")
    @patch("knowledge.permissions.Document.objects")
    def test_vector_permission_uses_persisted_type(self, documents, serializer, log):
        serializer.return_value.refresh.return_value = True
        for image, correct, wrong in [
            (True, P.KNOWLEDGE_IMAGE_VECTOR, P.KNOWLEDGE_DOCUMENT_VECTOR),
            (False, P.KNOWLEDGE_DOCUMENT_VECTOR, P.KNOWLEDGE_IMAGE_VECTOR),
        ]:
            documents.filter.return_value.exists.return_value = image
            DocumentView.Refresh().put(self.request(correct), document_id=self.document_id, **self.kwargs())
            with self.assertRaises(AppUnauthorizedFailed):
                DocumentView.Refresh().put(
                    self.request(wrong, query={"resource_type": "document" if image else "image"}),
                    document_id=self.document_id,
                    **self.kwargs(),
                )
        self.assertEqual(documents.filter.call_args.kwargs["knowledge__workspace_id"], self.workspace_id)

    @patch("common.log.log.Log")
    @patch("knowledge.views.document.DocumentSerializers.Batch")
    @patch("knowledge.permissions.Document.objects")
    def test_mixed_batch_requires_both_type_permissions(self, documents, serializer, log):
        documents.filter.return_value.values_list.return_value.distinct.return_value = ["image", "document"]
        serializer.return_value.batch_refresh.return_value = True
        data = {"id_list": [self.document_id], "resource_type": "image"}
        for permission in [P.KNOWLEDGE_IMAGE_VECTOR, P.KNOWLEDGE_DOCUMENT_VECTOR]:
            with self.assertRaises(AppUnauthorizedFailed):
                DocumentView.BatchRefresh().put(self.request(permission, data=data), **self.kwargs())
        DocumentView.BatchRefresh().put(
            self.request(P.KNOWLEDGE_IMAGE_VECTOR, P.KNOWLEDGE_DOCUMENT_VECTOR, data=data), **self.kwargs()
        )
        serializer.return_value.batch_refresh.assert_called_once()

    def test_old_permissions_do_not_grant_new_configuration_features(self):
        request = self.request(P.KNOWLEDGE_READ, P.KNOWLEDGE_EDIT, P.KNOWLEDGE_SYNC)
        for view, method in [
            (KnowledgeView.KnowledgeSyncSetting, "get"),
            (KnowledgeView.KnowledgeSyncSetting, "put"),
            (ExternalServiceView, "get"),
            (ExternalServiceView, "put"),
            (KnowledgeMcpConfigView, "get"),
        ]:
            with self.subTest(view=view.__name__, method=method), self.assertRaises(AppUnauthorizedFailed):
                getattr(view(), method)(request, **self.kwargs())

    @patch("knowledge.views.external_service.ExternalServiceSerializer")
    def test_mcp_config_has_its_own_permission_and_response(self, serializer):
        serializer.return_value.get_settings.return_value = {"mcp_config": {"test": True}, "enabled": True}
        response = KnowledgeMcpConfigView().get(self.request(P.KNOWLEDGE_MCP_CONFIG), **self.kwargs())
        self.assertEqual(json.loads(response.content)["data"], {"mcp_config": {"test": True}})

    @patch("knowledge.views.knowledge.KnowledgeSerializer.Operate")
    def test_detail_redaction_and_settings_section_permissions(self, serializer):
        serializer.return_value.one.side_effect = lambda: {
            "name": "test",
            "meta": {"app_secret": "example", "sync_setting": {}},
            "doc_strategy": {},
        }
        response = KnowledgeView.Operate().get(self.request(P.KNOWLEDGE_READ), **self.kwargs())
        self.assertEqual(json.loads(response.content)["data"]["meta"], {})
        for section, permission in [
            ("setting", P.KNOWLEDGE_SETTING_READ),
            ("document_strategy", P.KNOWLEDGE_DOCUMENT_STRATEGY_READ),
        ]:
            KnowledgeView.Operate().get(self.request(permission, query={"section": section}), **self.kwargs())
            with self.assertRaises(AppUnauthorizedFailed):
                KnowledgeView.Operate().get(self.request(P.KNOWLEDGE_READ, query={"section": section}), **self.kwargs())

    @patch("common.log.log.Log")
    @patch("knowledge.views.knowledge.KnowledgeSerializer.Operate")
    @patch("knowledge.permissions.Knowledge.objects")
    def test_setting_edits_preserve_omitted_metadata_and_reject_ungranted_changes(self, knowledge, serializer, log):
        stored = {"sync_setting": {"enabled": True}, "doc_strategy": {"test": True}}
        knowledge.filter.return_value.values_list.return_value.first.return_value = stored
        serializer.return_value.edit.side_effect = lambda payload: {**payload}
        request = self.request(P.KNOWLEDGE_SETTING_EDIT, data={"meta": {"source_url": "https://example.com"}})
        KnowledgeView.Operate().put(request, **self.kwargs())
        self.assertEqual(serializer.return_value.edit.call_args.args[0]["meta"]["sync_setting"], stored["sync_setting"])
        request.data["meta"]["sync_setting"] = {"enabled": False}
        with self.assertRaises(AppUnauthorizedFailed):
            KnowledgeView.Operate().put(request, **self.kwargs())


class _PermissionRows(list):
    def filter(self, **kwargs):
        return self

    def select_related(self, *args):
        return self

    def distinct(self):
        return self


class WorkspaceKnowledgePermissionMapTests(SimpleTestCase):
    @patch("common.auth.handle.impl.user_token.cache")
    @patch("common.auth.handle.impl.user_token.QuerySet")
    def test_role_and_resource_group_grants_keep_separate_subgroup_bitmaps(self, query, cache):
        from system_manage.models.workspace_user_group_permission import WorkspaceUserGroupResourcePermission
        from system_manage.models.workspace_user_permission import WorkspaceUserResourcePermission

        cache.get.return_value = None
        user_role_model, workspace_model, role_model, role_permission_model = (object() for _ in range(4))
        mappings = _PermissionRows([SimpleNamespace(workspace_id="ws", role_id="custom")])
        roles = _PermissionRows([SimpleNamespace(id="custom", type="USER")])
        role_permissions = _PermissionRows(
            [SimpleNamespace(role_id="custom", permission_id=str(P.KNOWLEDGE_IMAGE_READ.value))]
        )
        for auth_type, granted, expected in [
            (ResourceAuthType.ROLE, [], [P.KNOWLEDGE_IMAGE_READ]),
            (ResourceAuthType.RESOURCE_PERMISSION_GROUP, ["VIEW"], RESOURCE_PERMISSION_MAP["KNOWLEDGE_VIEW"]),
            (
                ResourceAuthType.RESOURCE_PERMISSION_GROUP,
                ["VIEW", "MANAGE"],
                RESOURCE_PERMISSION_MAP["KNOWLEDGE_VIEW"] + RESOURCE_PERMISSION_MAP["KNOWLEDGE_MANAGE"],
            ),
        ]:
            records = {
                user_role_model: mappings,
                role_model: roles,
                role_permission_model: role_permissions,
                WorkspaceUserResourcePermission: _PermissionRows(
                    [
                        SimpleNamespace(
                            auth_type=auth_type,
                            permission_list=granted,
                            workspace_id="ws",
                            target="kb",
                            auth_target_type="KNOWLEDGE",
                        )
                    ]
                ),
                WorkspaceUserGroupResourcePermission: _PermissionRows(),
            }
            query.side_effect = lambda model: records[model]
            bitmap = get_permissions(
                SimpleNamespace(id="user"), user_role_model, workspace_model, role_model, role_permission_model
            )
            request = SimpleNamespace(auth=SimpleNamespace(roles=[], permissions=bitmap))
            for permission in [p for p in P if p.value.group == Group.KNOWLEDGE]:
                with self.subTest(granted=granted, auth_type=auth_type, permission=permission.name):
                    self.assertEqual(
                        knowledge_permission(permission).hasPermission(request, workspace_id="ws", knowledge_id="kb"),
                        permission in expected,
                    )
