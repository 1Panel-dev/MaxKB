# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("knowledge", "0008_termbase"),
    ]

    operations = [
        migrations.AddField(
            model_name="knowledge",
            name="vector_store_type",
            field=models.CharField(
                choices=[("pg_vector", "PgVector"), ("qdrant", "Qdrant")],
                default="pg_vector",
                max_length=20,
                verbose_name="向量存储类型",
            ),
        ),
    ]
