# Generated by Django 4.2.15 on 2024-11-07 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0009_alter_document_status_alter_paragraph_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='meta',
            field=models.JSONField(default=dict, verbose_name='文件关联数据'),
        ),
    ]
