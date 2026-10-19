from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tools", "0008_toolworkflow_default_model_setting_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="toolworkflowversion",
            name="publish_desc",
            field=models.CharField(default="", max_length=1024, verbose_name="更新说明"),
        ),
    ]
