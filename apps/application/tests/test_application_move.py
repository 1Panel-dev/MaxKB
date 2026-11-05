from django.test import SimpleTestCase
from folders.tests.move_helpers import ResourceMoveTests
from application.models import ApplicationFolder
from application.serializers.application import ApplicationOperateSerializer
from application.views.application import ApplicationAPI


class ApplicationMoveTests(ResourceMoveTests, SimpleTestCase):
    domain = "application"
    view = ApplicationAPI
    view_module = "application.views.application"
    view_serializer = "application.views.application.ApplicationOperateSerializer"
    batch_view_serializer = "application.views.application.ApplicationBatchOperateSerializer"
    serializer_class = ApplicationOperateSerializer
    serializer_module = "application.serializers.application"
    serializer_id_key = "application_id"
    folder_model = ApplicationFolder
