import logging

import psycopg
from psycopg import sql
from django.db import migrations

from maxkb.const import CONFIG


def get_connect(db_name):
    return psycopg.connect(
        dbname=db_name,
        user=CONFIG.get('DB_USER'),
        password=CONFIG.get('DB_PASSWORD'),
        host=CONFIG.get('DB_HOST'),
        port=CONFIG.get('DB_PORT'),
        autocommit=True,
    )


def has_collation_version_mismatch(conn):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT datcollversion IS DISTINCT FROM pg_database_collation_actual_version(oid)
            FROM pg_database
            WHERE datname = current_database()
            """
        )
        result = cursor.fetchone()
        return result is not None and result[0]


def refresh_database_collation(db_name):
    with get_connect(db_name) as conn:
        if not has_collation_version_mismatch(conn):
            return
        with conn.cursor() as cursor:
            database_identifier = sql.Identifier(db_name)
            cursor.execute(sql.SQL("REINDEX DATABASE {}").format(database_identifier))
            cursor.execute(sql.SQL("ALTER DATABASE {} REFRESH COLLATION VERSION").format(database_identifier))


def refresh_collation(apps, schema_editor):
    app_db_name = CONFIG.get('DB_NAME')
    refresh_database_collation(app_db_name)
    if app_db_name == 'root':
        return
    try:
        refresh_database_collation('root')
    except Exception:
        logging.exception('Failed to refresh collation version for database root')


class Migration(migrations.Migration):
    dependencies = [
        ('system_manage', '0005_resourcemapping'),
    ]

    operations = [
        migrations.RunPython(refresh_collation, reverse_code=migrations.RunPython.noop, atomic=False),
    ]
