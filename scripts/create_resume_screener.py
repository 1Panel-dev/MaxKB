"""
简历自动筛选与初评助手 — 一键创建脚本

通过 MaxKB REST API 创建工作流应用，包含：
- 开始节点 → 文档提取 → 简历解析 → JD匹配评分 → 条件分支 → 三路回复

使用方法：
    uv run python scripts/create_resume_screener.py [--base-url URL] [--username USER] [--password PASS]
    
    如果后端不在 8080 端口，用 --base-url 指定后端地址（默认 http://localhost:8080）。
    如果前端不在 3000 端口，最终打印的 Chat URL 会不正确，但应用创建不受影响。

默认值：
    --base-url  http://localhost:8080
    --username  admin
    --password  MaxKB@123..
"""

import argparse
import json
import sys
from pathlib import Path

import requests

WORKFLOW_JSON_PATH = Path(__file__).resolve().parent.parent / "resume_screener_workflow.json"

CREATE_PAYLOAD_TEMPLATE = {
    "name": "简历自动筛选与初评助手",
    "desc": "上传简历并输入JD，自动完成简历解析、匹配评分和初评报告生成",
    "type": "WORK_FLOW",
    "prologue": "您好！我是简历自动筛选与初评助手。请粘贴职位描述（JD）并上传简历文件（PDF/Word），我将为您完成简历解析、匹配评分和初评报告生成。",
    "file_upload_enable": True,
    "file_upload_setting": {
        "max_file_size": 20971520,
        "file_suffix": ["pdf", "doc", "docx", "txt"]
    },
    "work_flow": None,
}


def login(base_url: str, username: str, password: str) -> str:
    resp = requests.post(
        f"{base_url}/admin/api/user/login",
        json={"username": username, "password": password},
        timeout=10,
    )
    body = resp.json()
    if body.get("code") != 200:
        print(f"Login failed: {body.get('message', body)}")
        sys.exit(1)
    token = body["data"]["token"]
    print(f"Logged in as '{username}'")
    return token


def get_workspace_id(base_url: str, token: str) -> str:
    resp = requests.get(
        f"{base_url}/admin/api/user/profile",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    body = resp.json()
    if body.get("code") != 200:
        print(f"Get profile failed: {body.get('message', body)}")
        sys.exit(1)
    workspace_list = body["data"].get("workspace_list", [])
    if not workspace_list:
        print("No workspace found in profile, using 'default'")
        return "default"
    ws_id = workspace_list[0]["id"]
    print(f"Workspace ID: {ws_id}")
    return ws_id


def create_application(base_url: str, token: str, workspace_id: str, workflow: dict) -> dict:
    payload = {**CREATE_PAYLOAD_TEMPLATE, "folder_id": workspace_id, "work_flow": workflow}
    resp = requests.post(
        f"{base_url}/admin/api/workspace/{workspace_id}/application",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    body = resp.json()
    if body.get("code") != 200:
        print(f"Create application failed: {body.get('message', body)}")
        sys.exit(1)
    app = body["data"]
    app_id = app["id"]
    print(f"Application created: {app['name']} (ID: {app_id})")
    return app


def publish_application(base_url: str, token: str, workspace_id: str, app_id: str):
    resp = requests.put(
        f"{base_url}/admin/api/workspace/{workspace_id}/application/{app_id}/publish",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    body = resp.json()
    if body.get("code") != 200:
        print(f"Publish failed: {body.get('message', body)}")
        sys.exit(1)
    print("Application published")


def get_access_token(base_url: str, token: str, workspace_id: str, app_id: str) -> str:
    resp = requests.get(
        f"{base_url}/admin/api/workspace/{workspace_id}/application/{app_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    body = resp.json()
    if body.get("code") != 200:
        print(f"Get application failed: {body.get('message', body)}")
        sys.exit(1)
    app = body["data"]
    return app.get("access_token", "")


def main():
    parser = argparse.ArgumentParser(description="Create resume screener app in MaxKB")
    parser.add_argument("--base-url", default="http://localhost:8080", help="MaxKB backend URL")
    parser.add_argument("--username", default="admin", help="Login username")
    parser.add_argument("--password", default="MaxKB@123..", help="Login password")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    if not WORKFLOW_JSON_PATH.exists():
        print(f"Workflow JSON not found at {WORKFLOW_JSON_PATH}")
        print("Run this script from the MaxKB project root directory.")
        sys.exit(1)

    with open(WORKFLOW_JSON_PATH) as f:
        workflow = json.load(f)

    print("=== Creating Resume Screener Application ===\n")

    token = login(base_url, args.username, args.password)
    workspace_id = get_workspace_id(base_url, token)
    app = create_application(base_url, token, workspace_id, workflow)
    publish_application(base_url, token, workspace_id, app["id"])
    access_token = get_access_token(base_url, token, workspace_id, app["id"])

    print(f"\n=== All Done! ===")
    print(f"Chat URL: {args.base_url.replace(':8080', ':3000')}/chat/{access_token}")
    print(f"Admin URL: {args.base_url.replace(':8080', ':3000')}/admin/#/application/detail/{app['id']}")


if __name__ == "__main__":
    main()
