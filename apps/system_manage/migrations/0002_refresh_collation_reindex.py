from django.db import migrations


def refresh_collation_and_reindex(apps, schema_editor):
    # 获取当前数据库名
    db_name = schema_editor.connection.settings_dict["NAME"]
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f'ALTER DATABASE "{db_name}" REFRESH COLLATION VERSION;')
        cursor.execute(f'REINDEX DATABASE "{db_name}";')


def noop(apps, schema_editor):
    # 不可逆操作，留空
    pass


class Migration(migrations.Migration):
    atomic = False  # ALTER DATABASE/REINDEX 需在事务外执行

    dependencies = [
        ("system_manage", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(refresh_collation_and_reindex, reverse_code=noop),
    ]