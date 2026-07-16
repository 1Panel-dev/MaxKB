import hashlib
import json
import uuid
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from application.models.application import Application, ApplicationTypeChoices
from application.models.application_access_token import ApplicationAccessToken

WORKFLOW_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent / "resume_screener_workflow.json"


class Command(BaseCommand):
    help = "创建简历自动筛选与初评助手（工作流应用）"

    def handle(self, *args, **options):
        if not WORKFLOW_PATH.exists():
            self.stderr.write(f"Workflow JSON not found at {WORKFLOW_PATH}")
            return

        with open(WORKFLOW_PATH) as f:
            workflow = json.load(f)

        with transaction.atomic():
            app_id = uuid.uuid4()
            app = Application(
                id=app_id,
                name="简历自动筛选与初评助手",
                desc="上传简历并输入JD，自动完成简历解析、匹配评分和初评报告生成",
                type=ApplicationTypeChoices.WORK_FLOW,
                prologue="您好！我是简历自动筛选与初评助手。请粘贴职位描述（JD）并上传简历文件（PDF/Word），我将为您完成简历解析、匹配评分和初评报告生成。",
                work_flow=workflow,
                file_upload_enable=True,
                file_upload_setting={
                    "max_file_size": 20971520,
                    "file_suffix": ["pdf", "doc", "docx", "txt"],
                },
                dialogue_number=0,
                model=None,
                model_setting={},
                user_id=None,
                is_publish=True,
                publish_time=timezone.now(),
                workspace_id="default",
            )
            app.save()

            access_token = ApplicationAccessToken(
                application=app,
                access_token=hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[8:24],
                is_active=True,
            )
            access_token.save()

        self.stdout.write(self.style.SUCCESS(f"Application created: {app.name} (ID: {app.id})"))
        self.stdout.write(self.style.SUCCESS(f"Chat URL: /chat/{access_token.access_token}"))
        self.stdout.write(
            self.style.SUCCESS(f"Admin URL: /admin/#/application/detail/{app.id}"))
