from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import SimpleTestCase

from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.database_model_manage.handle.impl import default_base_model_handle as handle
from system_manage.models import ResourceChatUserAuthorize, ResourceChatUserGroupAuthorize, ResourceType

KB_GROUP = "01a186b2-bed3-7cd0-9ba3-669bd89e59b1"
KB_USER = "01a186b2-bed3-7cd0-9ba3-669bd89e59b2"
KB_BOTH = "01a186b2-bed3-7cd0-9ba3-669bd89e59b3"
KB_NONE = "01a186b2-bed3-7cd0-9ba3-669bd89e59b4"


class DefaultModelHandleTest(SimpleTestCase):
    def test_community_settings_register_knowledge_authorization(self):
        self.assertIn(
            "common.database_model_manage.handle.impl.default_base_model_handle.DefaultBaseModelHandle",
            settings.MODEL_HANDLES,
        )
        with patch.object(DatabaseModelManage, "model_dict", {}):
            DatabaseModelManage.init()
            self.assertIs(
                DatabaseModelManage.get_model("get_knowledge_list_of_authorized"),
                handle.get_knowledge_list_of_authorized,
            )

    def test_knowledge_authorized_by_user_or_group(self):
        query_sets = {}

        def query_set(model):
            query_sets[model] = MagicMock()
            values = {
                ResourceChatUserGroupAuthorize: [KB_GROUP, KB_BOTH],
                ResourceChatUserAuthorize: [KB_USER, KB_BOTH],
            }.get(model, ["group-1"])
            query_sets[model].filter.return_value.values_list.return_value = values
            return query_sets[model]

        with patch.object(handle, "QuerySet", side_effect=query_set):
            result = handle.get_knowledge_list_of_authorized("user-1", [KB_GROUP, KB_USER, KB_BOTH, KB_NONE])

        self.assertEqual(result, [KB_GROUP, KB_USER, KB_BOTH])
        group_filter = query_sets[ResourceChatUserGroupAuthorize].filter.call_args.kwargs
        self.assertEqual(group_filter["resource_type"], ResourceType.KNOWLEDGE)
        self.assertTrue(group_filter["is_auth"])
        user_filter = query_sets[ResourceChatUserAuthorize].filter.call_args.kwargs
        self.assertEqual(
            (user_filter["user_id"], user_filter["resource_type"], user_filter["is_auth"]),
            ("user-1", ResourceType.KNOWLEDGE, True),
        )
