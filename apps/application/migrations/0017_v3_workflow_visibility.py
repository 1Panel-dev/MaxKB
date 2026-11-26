"""把 v2 工作流中引用本表单的显隐条件转换为 v3 格式，转换规则见 ``application.workflow.visibility_compat``。"""

from django.db import migrations

from application.workflow.visibility_compat import normalize_workflow_visibility

BATCH_SIZE = 500


def _normalize_model(model, db_alias):
    updates = []
    queryset = model.objects.using(db_alias).only("id", "work_flow")
    for obj in queryset.iterator(chunk_size=BATCH_SIZE):
        if normalize_workflow_visibility(obj.work_flow):
            updates.append(obj)
        if len(updates) >= BATCH_SIZE:
            model.objects.using(db_alias).bulk_update(updates, ["work_flow"])
            updates = []
    if updates:
        model.objects.using(db_alias).bulk_update(updates, ["work_flow"])


def forwards(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    for model_name in ("Application", "ApplicationVersion"):
        _normalize_model(apps.get_model("application", model_name), db_alias)


class Migration(migrations.Migration):
    dependencies = [
        ("application", "0016_v3_upgrade"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
