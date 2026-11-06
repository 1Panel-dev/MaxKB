import re

from django.db import migrations, models


def bind_active_share_files(apps, schema_editor):
    """Rebuild grants from active shares; unbound legacy grants are no longer trusted."""
    share_link_model = apps.get_model('application', 'ChatShareLink')
    chat_record_model = apps.get_model('application', 'ChatRecord')
    access_model = apps.get_model('knowledge', 'PublicFileAccess')
    alias = schema_editor.connection.alias
    links = share_link_model.objects.using(alias).filter(share_type='PUBLIC', chat__is_deleted=False)
    for link in links.iterator(chunk_size=500):
        file_ids = set()
        answers = chat_record_model.objects.using(alias).filter(
            chat_id=link.chat_id, id__in=link.chat_record_ids,
        ).values_list('answer_text_list', flat=True)
        for answer in answers.iterator(chunk_size=500):
            for group in answer or []:
                for item in group if isinstance(group, list) else [group]:
                    if isinstance(item, dict) and isinstance(item.get('content'), str):
                        file_ids.update(re.findall(r'\./oss/file/([\w-]+)', item['content']))
        access_model.objects.using(alias).bulk_create([
            access_model(source_type='FILE', source_id=file_id, share_link_id=link.id)
            for file_id in file_ids
        ], batch_size=500)


class Migration(migrations.Migration):
    dependencies = [
        ('knowledge', '0011_knowledgeworkflow_default_model_setting_and_more'),
        ('application', '0010_chatsharelink'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicfileaccess',
            name='share_link',
            field=models.ForeignKey(
                to='application.chatsharelink', on_delete=models.CASCADE,
                null=True, blank=True, verbose_name='分享链接',
            ),
        ),
        migrations.RunPython(bind_active_share_files, migrations.RunPython.noop),
    ]
