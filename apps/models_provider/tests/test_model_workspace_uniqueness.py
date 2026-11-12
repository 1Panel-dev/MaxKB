from unittest.mock import MagicMock, patch

from django.test import TestCase

from common.exception.app_exception import AppApiException
from models_provider.models import Model, Status
from models_provider.serializers.model_serializer import ModelSerializer
from users.models import User

MODEL_NAME = "zws-LLM-dp001"


class ModelWorkspaceUniquenessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="model-workspace-uniqueness-user",
            nick_name="Model workspace uniqueness user",
            password="password",
            role="ADMIN",
        )
        self.provider = MagicMock()
        self.provider.get_model_type_list.return_value = [{"value": "LLM"}]

    def create_model(self, workspace_id):
        return Model.objects.create(
            name=MODEL_NAME,
            status=Status.SUCCESS,
            model_type="LLM",
            model_name="deepseek-chat",
            user=self.user,
            provider="test_provider",
            credential="encrypted-credential",
            model_params_form=[],
            workspace_id=workspace_id,
        )

    def serializer_data(self, workspace_id):
        return {
            "user_id": str(self.user.id),
            "name": MODEL_NAME,
            "provider": "test_provider",
            "model_type": "LLM",
            "model_name": "deepseek-chat",
            "model_params_form": [],
            "credential": {"api_key": "secret"},
            "workspace_id": workspace_id,
        }

    def test_create_same_name_in_other_workspace_uses_insert_workspace(self):
        self.create_model("workspace-a")

        with (
            patch(
                "models_provider.serializers.model_serializer.ModelProvideConstants", {"test_provider": self.provider}
            ),
            patch("models_provider.serializers.model_serializer.UserResourcePermissionSerializer"),
        ):
            result = ModelSerializer.Create(data=self.serializer_data("workspace-a")).insert("workspace-b")

        self.assertEqual("workspace-b", Model.objects.get(id=result["id"]).workspace_id)

    def test_create_same_name_in_same_workspace_is_rejected(self):
        self.create_model("workspace-a")

        with (
            patch(
                "models_provider.serializers.model_serializer.ModelProvideConstants", {"test_provider": self.provider}
            ),
            self.assertRaises(AppApiException),
        ):
            ModelSerializer.Create(data=self.serializer_data("workspace-a")).insert("workspace-a")
