import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models

from application.models import Application
from common.mixins.app_model_mixin import AppModelMixin
from users.models import User


class ApplicationApiKey(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    secret_key = models.CharField(max_length=1024, verbose_name="秘钥", unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户id")
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, verbose_name="应用id")
    is_active = models.BooleanField(default=True, verbose_name="是否开启")
    allow_cross_domain = models.BooleanField(default=False, verbose_name="是否允许跨域")
    cross_domain_list = ArrayField(verbose_name="跨域列表",
                                   base_field=models.CharField(max_length=128, blank=True)
                                   , default=list)

    class Meta:
        db_table = "application_api_key"


class ApplicationPublicAccessClient(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    client_id = models.UUIDField(max_length=128, default=uuid.uuid1, verbose_name="公共访问链接客户端id")
    client_type = models.CharField(max_length=64, verbose_name="客户端类型")
    application = models.ForeignKey(Application, on_delete=models.CASCADE, verbose_name="应用id")
    access_num = models.IntegerField(default=0, verbose_name="访问总次数次数")
    intraday_access_num = models.IntegerField(default=0, verbose_name="当日访问次数")

    class Meta:
        db_table = "application_public_access_client"
        indexes = [
            models.Index(fields=['application_id', 'client_id']),
        ]
