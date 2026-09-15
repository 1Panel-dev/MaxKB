# coding=utf-8
"""
@project: MaxKB
@Author:  虎虎虎
@file:    skill.py
@date:    2026/9/15
@desc:
"""

import io
import json
import os
import zipfile

from asgiref.sync import sync_to_async
from django.db.models import QuerySet

from common.utils.rsa_util import rsa_long_decrypt
from knowledge.models import File
from tools.models import Tool


async def init_skills(skill_tool_ids, temp_dir):
    if not skill_tool_ids:
        return
    skills_dir = os.path.join(temp_dir, "skills")
    tools = await sync_to_async(lambda: list(QuerySet(Tool).filter(id__in=skill_tool_ids, is_active=True)))()
    if not tools:
        return

    for tool in tools:
        init_params_default_value = {i["field"]: i.get("default_value") for i in (tool.init_field_list or [])}
        if tool.init_params is not None:
            params = init_params_default_value | json.loads(rsa_long_decrypt(tool.init_params))
        else:
            params = init_params_default_value

        file = await sync_to_async(lambda t=tool: QuerySet(File).filter(id=t.code).first())()
        if not file:
            continue
        file_bytes = await sync_to_async(file.get_bytes)()

        with zipfile.ZipFile(io.BytesIO(file_bytes), "r") as zip_ref:
            members = [m for m in zip_ref.namelist() if not m.startswith("__MACOSX/") and "__MACOSX" not in m]
            for member in members:
                if ".." in member or member.startswith("/"):
                    raise ValueError(f"非法路径: {member}")
            zip_ref.extractall(skills_dir, members=members)

            # 获取技能解压后的顶级目录名
            top_level_dirs = set()
            for member in members:
                parts = member.split("/")
                if parts[0]:
                    top_level_dirs.add(parts[0])

            # 将 params 写入每个顶级目录下的 .env 文件
            if params:
                env_lines = [f"{key}={value}" for key, value in params.items()]
                env_content = "\n".join(env_lines) + "\n"
                for top_dir in top_level_dirs:
                    env_path = os.path.join(skills_dir, top_dir, ".env")
                    with open(env_path, "w", encoding="utf-8") as f:
                        f.write(env_content)

    os.system("chmod -R g+rx " + temp_dir)  # 确保技能目录可访问
