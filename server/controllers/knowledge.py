from fastapi import APIRouter, Request, UploadFile, File
from service.common import get_dict, set_dict
import requests
import shutil
import os
import json
from urllib.parse import quote
from httpx import AsyncClient
import uuid
import httpx

router = APIRouter(prefix="/knowledge")


@router.post("/get_settings")
async def get_settings():
    settings = {
        "knowledge_base": await get_dict("knowledge_base"),
        "api_base": await get_dict("api_base"),
        "api_base_token": await get_dict("api_base_token"),
    }
    return {"success": True, "message": "获取成功", "data": settings}


@router.post("/set_settings")
async def set_settings(request: Request):
    data = await request.json()
    await set_dict("knowledge_base", data["knowledge_base"])
    await set_dict("api_base", data["api_base"])
    await set_dict("api_base_token", data["api_base_token"])
    return {"success": True, "message": "设置成功"}


@router.post("/list")
async def list():
    knowledge_base = await get_dict("knowledge_base")
    api_base = await get_dict("api_base")
    api_base_token = await get_dict("api_base_token")
    if not knowledge_base:
        return {"success": True, "message": "获取成功", "data": []}
    bases = knowledge_base.split(",")

    async with AsyncClient() as client:
        url = f"{api_base}/datasets?page=1&limit=10000"
        headers = {"Authorization": f"Bearer {api_base_token}"}
        response = await client.get(url, headers=headers)
        result = response.json()

    data = []
    for base in bases:
        for item in result["data"]:
            if item["name"] == base:
                data.append(item)

    return {"success": True, "message": "获取成功", "data": data}


@router.post("/collection")
async def collection(request: Request):
    data = await request.json()
    api_base = await get_dict("api_base")
    api_base_token = await get_dict("api_base_token")
    url = f"{api_base}/datasets/{data["id"]}/documents?page=1&limit=10000"
    headers = {"Authorization": f"Bearer {api_base_token}"}
    async with AsyncClient() as client:
        response = await client.get(url, headers=headers)
        result = response.json()
    return {"success": True, "message": "获取成功", "data": result["data"]}


@router.post("/remove_collection")
async def remove_collection(request: Request):
    data = await request.json()
    api_base = await get_dict("api_base")
    api_base_token = await get_dict("api_base_token")
    url = f"{api_base}/datasets/{data["dataset_id"]}/documents/{data["document_id"]}"
    headers = {"Authorization": f"Bearer {api_base_token}"}
    async with AsyncClient() as client:
        response = await client.delete(url, headers=headers)
    result = response.json()
    return {"success": True, "message": "删除成功", "data": result}


@router.post("/add_file_collection")
async def add_file_collection(request: Request):
    data = await request.json()
    api_base = await get_dict("api_base")
    api_base_token = await get_dict("api_base_token")
    url = f"{api_base}/datasets/{data["dataset_id"]}/document/create-by-file"
    headers = {"Authorization": f"Bearer {api_base_token}"}
    send_data = {"data": json.dumps({"indexing_technique": "high_quality"})}
    for file in data["files"]:
        files = {
            "file": (os.path.basename(file), open(file, "rb")),
        }
        async with AsyncClient() as client:
            response = await client.post(
                url, data=send_data, files=files, headers=headers
            )
    return {"success": True, "message": "添加成功"}


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    file_location = f"{upload_dir}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"success": True, "message": "上传成功", "data": file_location}
