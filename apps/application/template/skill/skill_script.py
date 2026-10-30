#!/usr/bin/env python3
"""Call MaxKB applications as a chat user: manage local conversations, chat, download files. Standard library only."""

import argparse
import json
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PATTERN = re.compile(r"oss/file/([\w-]+)")
# 本地会话记录：{application_id: {"current": chat_id, "chats": [{chat_id, title, created_at}]}}
STATE_PATH = os.path.join(SKILL_DIR, ".maxkb_state.json")
TITLE_LENGTH = 50


def load_env():
    env_path = os.path.join(SKILL_DIR, ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def get_config():
    load_env()
    base_url = os.environ.get("MAXKB_BASE_URL", "").rstrip("/")
    api_key = os.environ.get("MAXKB_API_KEY", "")
    if not base_url or not api_key:
        sys.exit("MAXKB_BASE_URL and MAXKB_API_KEY must be set (see .env)")
    return base_url, api_key


def open_url(request, base_url):
    try:
        return urllib.request.urlopen(request, timeout=600)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
    except urllib.error.URLError as e:
        sys.exit(f"Cannot reach {base_url}: {e.reason}")


def print_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def get_application_id(args):
    load_env()
    application_id = args.application_id or os.environ.get("MAXKB_APPLICATION_ID", "")
    if not application_id:
        sys.exit("Pass --application-id or set MAXKB_APPLICATION_ID (see .env)")
    return application_id


def load_state():
    if not os.path.exists(STATE_PATH):
        return {}
    with open(STATE_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    # 先写临时文件再替换，避免中断时留下半个 JSON
    fd, tmp_path = tempfile.mkstemp(dir=SKILL_DIR, prefix=".maxkb_state.")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, STATE_PATH)


def new_chat(app_state, title=""):
    # 新会话由客户端生成 chat_id，服务端首次对话时创建；未指定标题时由第一条消息补上
    chat = {"chat_id": str(uuid.uuid4()), "title": title, "created_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    app_state.setdefault("chats", []).append(chat)
    app_state["current"] = chat["chat_id"]
    return chat


def list_chats(app_state):
    current = app_state.get("current")
    return [
        {"index": index, **chat, "current": chat["chat_id"] == current}
        for index, chat in enumerate(app_state.get("chats") or [], start=1)
    ]


def find_chat(app_state, key):
    """按 `chats` 中的序号或 chat_id 查找本地会话"""
    chat = next(
        (
            chat
            for index, chat in enumerate(app_state.get("chats") or [], start=1)
            if key in (str(index), chat["chat_id"])
        ),
        None,
    )
    if chat is None:
        sys.exit(f"Conversation {key} not found; run `chats` to see the local conversations")
    return chat


def open_chat(args):
    application_id = get_application_id(args)
    state = load_state()
    chat = new_chat(state.setdefault(application_id, {}), args.title or "")
    save_state(state)
    print_json({"application_id": application_id, "chat_id": chat["chat_id"], "title": chat["title"]})


def chats(args):
    application_id = get_application_id(args)
    app_state = load_state().get(application_id, {})
    print_json({"application_id": application_id, "current": app_state.get("current"), "chats": list_chats(app_state)})


def switch_chat(args):
    application_id = get_application_id(args)
    state = load_state()
    app_state = state.get(application_id, {})
    target = find_chat(app_state, args.chat)
    app_state["current"] = target["chat_id"]
    save_state(state)
    print_json({"application_id": application_id, "chat_id": target["chat_id"], "title": target["title"]})


def rename_chat(args):
    application_id = get_application_id(args)
    state = load_state()
    target = find_chat(state.get(application_id, {}), args.chat)
    target["title"] = args.title
    save_state(state)
    print_json({"application_id": application_id, "chat_id": target["chat_id"], "title": target["title"]})


def read_stream(response):
    """读取 SSE：TEXT/HTML 分片按顺序拼成回答，FAILURE 收集为错误，直到 [DONE]"""
    answer, errors = [], []
    for raw_line in response:
        line = raw_line.decode("utf-8", errors="replace").strip()
        if not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if payload == "[DONE]":
            break
        try:
            frame = json.loads(payload)
        except json.JSONDecodeError:
            continue
        for block in frame.get("content") or []:
            if block.get("type") in ("TEXT", "HTML"):
                answer.append(block.get("content") or "")
            elif block.get("type") == "FAILURE":
                errors.append(block.get("content") or "")
    return "".join(answer), errors


def chat(args):
    base_url, api_key = get_config()
    application_id = get_application_id(args)
    state = load_state()
    app_state = state.setdefault(application_id, {})
    current = next((c for c in app_state.get("chats") or [] if c["chat_id"] == app_state.get("current")), None)
    if current is None:
        current = new_chat(app_state)
    if not current["title"]:
        current["title"] = args.message[:TITLE_LENGTH]
    save_state(state)
    chat_id = current["chat_id"]
    payload = {"message": {"content": args.message}, "stream": True, "form_data": json.loads(args.form_data)}
    request = urllib.request.Request(
        f"{base_url}/api/v3/application/{application_id}/chat/{chat_id}/chat_message",
        data=json.dumps(payload).encode("utf-8"),
        # 不带 Accept: text/event-stream，DRF 内容协商只支持 JSON 渲染器，会拒绝该请求
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    with open_url(request, base_url) as response:
        if "text/event-stream" not in response.headers.get("Content-Type", ""):
            # 校验失败等情况在开始流式输出前以 JSON 返回
            data = json.loads(response.read().decode("utf-8"))
            sys.exit(f"MaxKB error {data.get('code')}: {data.get('message')}")
        answer, errors = read_stream(response)
    result = {"application_id": application_id, "chat_id": chat_id, "answer": answer}
    if errors:
        result["errors"] = errors
    print_json(result)
    if errors:
        sys.exit(1)


def download(args):
    base_url, api_key = get_config()
    match = FILE_PATTERN.search(args.file)
    file_id = match.group(1) if match else args.file
    request = urllib.request.Request(f"{base_url}/oss/file/{file_id}", headers={"Cookie": f"mk_file_auth={api_key}"})
    with open_url(request, base_url) as response:
        disposition = response.headers.get("Content-Disposition", "")
        name_match = re.search(r"filename=\"?([^\";]+)\"?", disposition)
        file_name = os.path.basename(urllib.parse.unquote(name_match.group(1))) if name_match else file_id
        os.makedirs(args.output_dir, exist_ok=True)
        path = os.path.join(args.output_dir, file_name)
        with open(path, "wb") as f:
            f.write(response.read())
    print_json({"file_id": file_id, "path": os.path.abspath(path)})


def main():
    parser = argparse.ArgumentParser(description="MaxKB application skill")
    subparsers = parser.add_subparsers(dest="command", required=True)

    application_help = "Application to use; defaults to MAXKB_APPLICATION_ID"

    open_parser = subparsers.add_parser("open", help="Start a new conversation and make it current")
    open_parser.add_argument("--title", help="Conversation title; defaults to the first message")
    open_parser.add_argument("--application-id", help=application_help)
    open_parser.set_defaults(func=open_chat)

    chats_parser = subparsers.add_parser("chats", help="List local conversations")
    chats_parser.add_argument("--application-id", help=application_help)
    chats_parser.set_defaults(func=chats)

    switch_parser = subparsers.add_parser("switch", help="Make a local conversation current")
    switch_parser.add_argument("chat", help="Index from `chats`, or a chat_id")
    switch_parser.add_argument("--application-id", help=application_help)
    switch_parser.set_defaults(func=switch_chat)

    rename_parser = subparsers.add_parser("rename", help="Change the title of a local conversation")
    rename_parser.add_argument("chat", help="Index from `chats`, or a chat_id")
    rename_parser.add_argument("title", help="New title")
    rename_parser.add_argument("--application-id", help=application_help)
    rename_parser.set_defaults(func=rename_chat)

    chat_parser = subparsers.add_parser("chat", help="Send a message in the current conversation")
    chat_parser.add_argument("message", help="Question or instruction for the application")
    chat_parser.add_argument("--application-id", help=application_help)
    chat_parser.add_argument("--form-data", default="{}", help="JSON object of application input fields")
    chat_parser.set_defaults(func=chat)

    download_parser = subparsers.add_parser("download", help="Download a file returned by the application")
    download_parser.add_argument("file", help="File ID or file link (containing oss/file/<id>)")
    download_parser.add_argument("--output-dir", default=".", help="Directory to save the file in")
    download_parser.set_defaults(func=download)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
