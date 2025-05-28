from fastapi import APIRouter, Request
from models import Account, App, History
from uuid import uuid4
from service.common import get_dict
import requests
from datetime import datetime
from httpx import AsyncClient
import os

router = APIRouter(prefix="/client")


@router.post("/login")
async def login(request: Request):
    data = await request.json()
    account = await Account.get_or_none(
        account=data.get("account"), password=data.get("password")
    )
    if not account:
        return {"success": False, "message": "账号或密码错误"}
    token = uuid4()
    account.token = str(token)
    await account.save(update_fields=["token"])
    return {"success": True, "message": "登录成功", "data": account}


@router.post("/check")
async def logout(request: Request):
    token = request.headers.get("token")
    if not token:
        return {"success": False, "message": "尚未登录"}
    account = await Account.get_or_none(token=token)
    if account:
        return {"success": True, "message": "已登录"}
    else:
        return {"success": False, "message": "尚未登录"}


@router.post("/chat")
async def chat(request: Request):
    api_base = await get_dict("api_base")
    if not api_base:
        return {"success": False, "message": "请先在后台配置api地址"}

    data = await request.json()

    app_id = data.get("app_id")
    app = await App.get_or_none(id=app_id)

    if not app:
        return {"success": False, "message": "应用不存在"}

    token = app.token
    account_id = data.get("account_id")
    chatid = data.get("chatid")
    question = data.get("question")
    history = {
        "account_id": account_id,
        "app_id": app_id,
        "question": question,
        "question_time": datetime.now(),
    }
    url = f"{api_base}/chat-messages"
    data = {
        "user": account_id,
        "inputs": {},
        "query": question,
        "response_mode": "blocking",
    }
    headers = {
        "Authorization": f"Bearer {token}",
    }
    async with AsyncClient(timeout=None) as client:
        res = await client.post(url, json=data, headers=headers)
        res = res.json()
    text = res.get("answer", None)
    if not text:
        return {
            "success": False,
            "message": "聊天失败，未获取到回答",
            "data": "服务器异常",
        }
    history["answer"] = text
    history["answer_time"] = datetime.now()
    await History.create(**history)
    return {"success": True, "message": "聊天成功", "data": text}


@router.post("/zk")
async def zk(request: Request):
    data = await request.json()

    appid = data.get("appid", None)
    if not appid:
        return {"success": False, "message": "请提供appid"}
    type = data.get("type", None)
    if not type:
        return {"success": False, "message": "请提供type"}
    content = data.get("content", None)
    if not content:
        return {"success": False, "message": "请提供content"}

    api_base = await get_dict("api_base")
    if not api_base:
        return {"success": False, "message": "请先在后台配置api地址"}

    app = await App.get_or_none(id=appid)

    if not app:
        return {"success": False, "message": "应用不存在"}

    token = app.token

    async def upload_file(file_path, user):
        upload_url = f"{api_base}/files/upload"
        headers = {
            "Authorization": f"Bearer {token}",
        }

        with open(file_path, "rb") as file:
            files = {"file": (os.path.basename(file_path), file)}
            data = {"user": user, "type": "XLSX"}
            async with AsyncClient(timeout=None) as client:
                res = await client.post(
                    upload_url, headers=headers, files=files, data=data
                )
        return res.json().get("id")

    async def run_workflow(file_id, type, content, user, response_mode="blocking"):
        workflow_url = f"{api_base}/workflows/run"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        data = {
            "inputs": {
                "file": {
                    "transfer_method": "local_file",
                    "upload_file_id": file_id,
                    "type": "document",
                },
                "type": type,
                "content": content,
            },
            "response_mode": response_mode,
            "user": user,
        }
        async with AsyncClient(timeout=None) as client:
            res = await client.post(workflow_url, headers=headers, json=data)
        return res.json()

    file_id = await upload_file("assets/zkgz.xlsx", "zk")
    if not file_id:
        return {"success": False, "message": "上传文件失败"}
    result = await run_workflow(file_id, type, content, "zk")

    return {"success": True, "message": "运行内涵质控工作流成功", "data": result}
