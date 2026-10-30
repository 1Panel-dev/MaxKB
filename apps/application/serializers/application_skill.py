# coding=utf-8
"""
@project: MaxKB
@file:    application_skill.py
@desc:    将应用导出为 Skills 压缩包
"""

import io
import json
import os
import re
import zipfile
from urllib.parse import urlsplit

from django.utils.translation import gettext_lazy as _
from rest_framework import status

from common.exception.app_exception import AppApiException
from maxkb.conf import PROJECT_DIR
from maxkb.const import CONFIG

SKILL_SCRIPT_PATH = os.path.join(PROJECT_DIR, "apps", "application", "template", "skill", "skill_script.py")


class InvalidSkillBaseUrl(AppApiException):
    # 以 400 返回，前端据此让用户手动填写访问地址
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, _("Invalid MaxKB address"))


def get_chat_base_url(site_url):
    """校验 MaxKB 站点地址（协议 + 主机 + 端口，可带路径前缀）并拼上对话路径。
    地址会写入 .env，必须拒绝换行等字符，避免注入额外配置"""
    site_url = (site_url or "").strip()
    if not site_url or re.search(r"\s", site_url):
        raise InvalidSkillBaseUrl()
    try:
        parts = urlsplit(site_url)
        parts.port  # 非法端口在此抛出 ValueError
    except ValueError:
        raise InvalidSkillBaseUrl()
    if parts.scheme not in ("http", "https") or not parts.hostname or parts.query or parts.fragment:
        raise InvalidSkillBaseUrl()
    return f"{site_url.rstrip('/')}{CONFIG.get_chat_path()}"


def get_skill_name(application):
    # Skills 规范要求 name 仅含小写字母、数字和连字符，中文名称回退为应用 ID
    name = re.sub(r"[^a-z0-9]+", "-", (application.name or "").lower()).strip("-")
    return (name or f"application-{str(application.id)[:8]}")[:64]


def get_user_input_fields(application):
    nodes = (application.work_flow or {}).get("nodes") or []
    base_node = next((n for n in nodes if n.get("type") == "base-node"), None)
    if base_node is None:
        return []
    return (base_node.get("properties") or {}).get("user_input_field_list") or []


def build_skill_md(application, skill_name):
    description = " ".join((application.desc or application.name or "").split())
    description = f'{description} Use this skill to ask the MaxKB application "{application.name}".'[:1024]
    lines = [
        "---",
        f"name: {skill_name}",
        # JSON 字符串即合法的 YAML 双引号字符串，避免描述中的冒号等字符破坏 frontmatter
        f"description: {json.dumps(description, ensure_ascii=False)}",
        "---",
        "",
        f"# {application.name}",
        "",
    ]
    if application.desc:
        lines += [application.desc, ""]
    lines += [
        "## Commands",
        "",
        "The script keeps a local list of conversations and a current conversation in "
        "`.maxkb_state.json` in this skill's directory, per application. "
        "Every command accepts `--application-id <id>` (defaults to `MAXKB_APPLICATION_ID`).",
        "",
        "### chat",
        "",
        "Send one message in the current conversation. If there is no current conversation, a new one is "
        "started and becomes current.",
        "",
        "```bash",
        f"python {skill_name}/scripts/maxkb.py chat \"<message>\" [--form-data '<json>']",
        "```",
        "",
        "- `--form-data`: JSON object of application input fields",
        "",
        "Prints JSON `{application_id, chat_id, answer}`. On application failure it also has `errors` "
        "and exits with code 1.",
        "",
        "### open",
        "",
        "Start a new conversation and make it current.",
        "",
        "```bash",
        f'python {skill_name}/scripts/maxkb.py open [--title "<title>"]',
        "```",
        "",
        "- `--title`: conversation title; defaults to the first message sent in it",
        "",
        "Prints JSON `{application_id, chat_id, title}`.",
        "",
        "### chats",
        "",
        "List the local conversations, oldest first.",
        "",
        "```bash",
        f"python {skill_name}/scripts/maxkb.py chats",
        "```",
        "",
        "Prints JSON `{application_id, current, chats: [{index, chat_id, title, created_at, current}]}`. "
        "`title` is the title given to `open` or `rename`, otherwise the first message of the conversation.",
        "",
        "### switch",
        "",
        "Make a local conversation current.",
        "",
        "```bash",
        f"python {skill_name}/scripts/maxkb.py switch <index or chat_id>",
        "```",
        "",
        "Prints JSON `{application_id, chat_id, title}`.",
        "",
        "### rename",
        "",
        "Change the title of a local conversation.",
        "",
        "```bash",
        f'python {skill_name}/scripts/maxkb.py rename <index or chat_id> "<title>"',
        "```",
        "",
        "Prints JSON `{application_id, chat_id, title}`.",
        "",
        "### download",
        "",
        "Download a MaxKB file.",
        "",
        "```bash",
        f"python {skill_name}/scripts/maxkb.py download <file_id or link> [--output-dir <dir>]",
        "```",
        "",
        "- `<file_id or link>`: a file ID, or a link containing `oss/file/<file_id>` (e.g. `./oss/file/<id>`)",
        "- `--output-dir`: defaults to the current directory",
        "",
        "Prints JSON `{file_id, path}`.",
        "",
    ]
    fields = get_user_input_fields(application)
    if fields:
        lines += [
            "## Input fields",
            "",
            "Pass these as a JSON object with `--form-data`:",
            "",
        ]
        for field in fields:
            label = field.get("label")
            if isinstance(label, dict):
                label = label.get("label")
            required = "required" if field.get("required") else "optional"
            lines.append(f"- `{field.get('field')}` ({required}): {label or ''}".rstrip(": "))
        lines.append("")
    lines += [
        "## Configuration",
        "",
        "Set `MAXKB_API_KEY` in `.env` to the chat user's API key (starting with `chat-`, created in the chat "
        "page's user settings). The chat user must have access to this application. "
        "Adjust `MAXKB_BASE_URL` if the MaxKB chat page is reached through another address.",
        "",
    ]
    return "\n".join(lines)


def build_env(application, base_url):
    return "\n".join(
        [
            f"MAXKB_BASE_URL={base_url}",
            f"MAXKB_APPLICATION_ID={application.id}",
            "MAXKB_API_KEY=",
            "",
        ]
    )


def build_application_skill_zip(application, base_url):
    """返回 (技能名称, zip 字节)。base_url 为对话入口地址，如 http://host/chat"""
    skill_name = get_skill_name(application)
    with open(SKILL_SCRIPT_PATH, encoding="utf-8") as f:
        script = f.read()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(f"{skill_name}/SKILL.md", build_skill_md(application, skill_name))
        zip_file.writestr(f"{skill_name}/scripts/maxkb.py", script)
        zip_file.writestr(f"{skill_name}/.env", build_env(application, base_url))
    return skill_name, buffer.getvalue()
