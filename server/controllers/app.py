from fastapi import APIRouter, Request, Depends
from models import App
from fastapi_pagination import Params
from fastapi_pagination.ext.tortoise import paginate
from dtos.common import DataList, AppPydantic

router = APIRouter(prefix="/app")


@router.post("/add")
async def add(request: Request):
    data = await request.json()
    app = await App.create(**data)
    return {"success": True, "message": "添加成功", "data": app}


@router.post("/remove")
async def remove(request: Request):
    data = await request.json()
    app = await App.get_or_none(id=data["id"])
    if not app:
        return {"success": False, "message": "应用不存在"}
    await app.delete()
    return {"success": True, "message": "删除成功"}


@router.post("/remove_batch")
async def remove_batch(request: Request):
    data = await request.json()
    await App.filter(id__in=data["ids"]).delete()
    return {"success": True, "message": "删除成功"}


@router.post("/update")
async def update(request: Request):
    data = await request.json()
    app = await App.get_or_none(id=data["id"])
    if not app:
        return {"success": False, "message": "应用不存在"}
    await app.update_from_dict(data)
    del data["id"]
    await app.save(update_fields=data.keys())
    return {"success": True, "message": "更新成功"}


@router.post("/get")
async def get(request: Request):
    data = await request.json()
    app = await App.get_or_none(id=data["id"])
    if not app:
        return {"success": False, "message": "应用不存在"}
    return {"success": True, "message": "获取成功", "data": app}


@router.post("/all")
async def all(request: Request):
    apps = await App.all()
    return {"success": True, "message": "获取成功", "data": apps}


@router.post("/list", response_model=DataList[AppPydantic])
async def list(params: Params = Depends()):
    apps = await paginate(App.all().order_by("-id"), params)
    result = DataList[AppPydantic](success=True, message="获取成功", data=apps)
    return result
