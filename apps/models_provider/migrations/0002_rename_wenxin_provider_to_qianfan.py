from django.db import migrations

OLD_PROVIDER = "model_wenxin_provider"
NEW_PROVIDER = "model_qianfan_provider"


def forwards(apps, schema_editor):
    Model = apps.get_model("models_provider", "Model")
    Model.objects.filter(provider=OLD_PROVIDER).update(provider=NEW_PROVIDER)


def backwards(apps, schema_editor):
    Model = apps.get_model("models_provider", "Model")
    Model.objects.filter(provider=NEW_PROVIDER).update(provider=OLD_PROVIDER)


class Migration(migrations.Migration):
    dependencies = [
        ("models_provider", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
