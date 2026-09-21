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
    ]
