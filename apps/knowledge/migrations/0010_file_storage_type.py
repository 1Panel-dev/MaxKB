from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("knowledge", "0009_document_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="file",
            name="storage_type",
            field=models.CharField(db_index=True, default="pg", max_length=16),
        ),
        migrations.AlterField(
            model_name="file",
            name="loid",
            field=models.IntegerField(blank=True, null=True, verbose_name="loid"),
        ),
    ]
