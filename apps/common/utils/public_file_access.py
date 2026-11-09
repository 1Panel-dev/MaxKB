# coding=utf-8
"""Bind public file grants to live shares using the existing authorization table."""
from uuid import UUID

from django.db import connections

from application.models import ChatShareLink, ShareLinkType
from knowledge.models import PublicFileAccess


def public_share_file_source_id(file_id, share_link_id):
    # Two UUIDs and a separator fit the existing source_id field (max_length=128).
    return f'{UUID(str(file_id))}:{UUID(str(share_link_id))}'


def has_active_public_file_share(file_id):
    prefix = f'{UUID(str(file_id))}:'
    share_ids = set()
    source_ids = PublicFileAccess.objects.filter(
        source_type='FILE', source_id__startswith=prefix,
    ).values_list('source_id', flat=True)
    for source_id in source_ids.iterator():
        try:
            share_ids.add(UUID(source_id[len(prefix):]))
        except ValueError:
            continue
    return bool(share_ids) and ChatShareLink.objects.filter(
        id__in=share_ids, share_type=ShareLinkType.PUBLIC, chat__is_deleted=False,
    ).exists()


def delete_public_share_file_access(share_link, using):
    PublicFileAccess.objects.using(using).filter(
        source_type='FILE', source_id__endswith=f':{share_link.id}',
    ).delete()

    # Deployments that already ran the removed 0012 migration may retain its nullable FK.
    # Delete only this share's legacy rows before deleting the share; no schema changes are needed.
    connection = connections[using]
    table = PublicFileAccess._meta.db_table
    with connection.cursor() as cursor:
        columns = connection.introspection.get_table_description(cursor, table)
        if any(column.name == 'share_link_id' for column in columns):
            quote = connection.ops.quote_name
            share_id = share_link._meta.pk.get_db_prep_value(share_link.id, connection)
            cursor.execute(
                f'DELETE FROM {quote(table)} WHERE {quote("share_link_id")} = %s', [share_id],
            )
