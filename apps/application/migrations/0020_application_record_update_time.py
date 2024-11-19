from django.db import migrations, connection

batch_update_update_time = """
UPDATE application_chat ac
SET update_time = acr_max.max_update_time
FROM (
    SELECT chat_id, MAX(update_time) AS max_update_time
    FROM application_chat_record
    GROUP BY chat_id
) acr_max
WHERE ac.id = acr_max.chat_id;
"""


class Migration(migrations.Migration):
    dependencies = [
        ('application', '0019_application_file_upload_enable_and_more'),
    ]

    operations = [
        migrations.RunSQL(batch_update_update_time),
    ]
