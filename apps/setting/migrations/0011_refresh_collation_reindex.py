import logging

import psycopg
from django.db import migrations

from smartdoc.const import CONFIG


def get_connect(db_name):
    conn_params = {
        "dbname": db_name,
        "user": CONFIG.get('DB_USER'),
        "password": CONFIG.get('DB_PASSWORD'),
        "host": CONFIG.get('DB_HOST'),
        "port": CONFIG.get('DB_PORT')
    }
    # 建立连接
    connect = psycopg.connect(**conn_params)
    return connect


def sql_execute(conn, reindex_sql: str, alter_database_sql: str):
    """
    执行一条sql
    @param reindex_sql:
    @param conn:
    @param alter_database_sql:
    """
    conn.autocommit = True
    with conn.cursor() as cursor:
        cursor.execute(reindex_sql, [])
        cursor.execute(alter_database_sql, [])
        cursor.close()

def re_index(apps, schema_editor):
    app_db_name = CONFIG.get('DB_NAME')
    try:
        re_index_database(app_db_name)
    except Exception as e:
        logging.error(f'reindex database {app_db_name}发送错误:{str(e)}')
    try:
        re_index_database('root')
    except Exception as e:
        logging.error(f'reindex database root 发送错误:{str(e)}')


def re_index_database(db_name):
    db_conn = get_connect(db_name)
    sql_execute(db_conn, f'REINDEX DATABASE "{db_name}";', f'ALTER DATABASE "{db_name}" REFRESH COLLATION VERSION;')
    db_conn.close()


class Migration(migrations.Migration):

    dependencies = [
        ('setting', '0010_log'),
    ]

    operations = [
        migrations.RunPython(re_index, atomic=False)
    ]
