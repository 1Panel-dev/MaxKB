from django.db import migrations, models

from knowledge.models.knowledge import default_external_service


class Migration(migrations.Migration):
    dependencies = [("knowledge", "0014_knowledgeworkflow_default_model_setting_and_more")]

    operations = [
        # An absent authentication setting preserves existing internal access rules.
        migrations.AddField(
            model_name="knowledge",
            name="external_service",
            field=models.JSONField(default=dict, verbose_name="外部检索服务"),
        ),
        migrations.AlterField(
            model_name="knowledge",
            name="external_service",
            field=models.JSONField(default=default_external_service, verbose_name="外部检索服务"),
        ),
        migrations.AlterField(
            model_name="knowledgesynclog",
            name="status",
            field=models.CharField(
                choices=[
                    ("running", "同步中"),
                    ("success", "同步成功"),
                    ("failure", "同步失败"),
                    ("skipped", "已跳过"),
                ],
                db_index=True,
                default="running",
                max_length=16,
                verbose_name="同步状态",
            ),
        ),
    ]
