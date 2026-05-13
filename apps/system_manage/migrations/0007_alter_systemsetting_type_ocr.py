# coding=utf-8
"""
    @project: maxkb
    @file: 0007_alter_systemsetting_type_ocr.py
    @desc: 为 SystemSetting.type 新增 OCR=4 选项。
"""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('system_manage', '0006_alter_systemsetting_type_theme'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemsetting',
            name='type',
            field=models.IntegerField(
                choices=[
                    (0, '邮箱'),
                    (1, '私钥秘钥'),
                    (2, '日志清理时间'),
                    (3, '外观设置'),
                    (4, 'OCR 设置'),
                ],
                default=0,
                primary_key=True,
                serialize=False,
                verbose_name='设置类型',
            ),
        ),
    ]
