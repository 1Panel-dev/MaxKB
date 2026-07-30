# Generated for Milvus vector store support

from django.db import migrations

import knowledge.models.knowledge


class Migration(migrations.Migration):
    dependencies = [
        ("knowledge", "0015_knowledge_external_service"),
    ]

    operations = [
        # Milvus 混合存储模式下，向量交由 Milvus 保存，PG 的 embedding 列允许为空。
        # pg_vector 模式不受影响（仍写入真实向量）。
        migrations.AlterField(
            model_name="embedding",
            name="embedding",
            field=knowledge.models.knowledge.VectorField(null=True, verbose_name="向量"),
        ),
    ]
