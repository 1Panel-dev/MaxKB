# coding=utf-8
"""
    @project: maxkb
    @file: 0006_alter_systemsetting_type_theme.py
    @desc: 为 SystemSetting.type 新增 THEME=3 选项，承载外观设置（白标）配置。
"""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('system_manage', '0005_resourcemapping'),
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
                ],
                default=0,
                primary_key=True,
                serialize=False,
                verbose_name='设置类型',
            ),
        ),
    ]
