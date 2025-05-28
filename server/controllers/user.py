from fastapi import APIRouter, Request, Depends
from fastapi_pagination import Params
from fastapi_pagination.ext.tortoise import paginate
from models import User
from dtos.common import DataList, UserPydantic

router = APIRouter(prefix="/user")


@router.post("/add")
async def add(request: Request):
    data = await request.json()
    user = await User.create(**data)
    return {"success": True, "message": "添加成功", "data": user}


@router.post("/remove")
async def remove(request: Request):
    data = await request.json()
    user = await User.get_or_none(id=data["id"])
    if not user:
        return {"success": False, "message": "应用不存在"}
    await user.delete()
    return {"success": True, "message": "删除成功"}


@router.post("/remove_batch")
async def remove_batch(request: Request):
    data = await request.json()
    await User.filter(id__in=data["ids"]).delete()
    return {"success": True, "message": "删除成功"}


@router.post("/update")
async def update(request: Request):
    data = await request.json()
    user = await User.get_or_none(id=data["id"])
    if not user:
        return {"success": False, "message": "应用不存在"}
    await user.update_from_dict(data)
    del data["id"]
    await user.save(update_fields=data.keys())
    return {"success": True, "message": "更新成功"}


@router.post("/get")
async def get(request: Request):
    data = await request.json()
    user = await User.get_or_none(id=data["id"])
    if not user:
        return {"success": False, "message": "应用不存在"}
    return {"success": True, "message": "获取成功", "data": user}


@router.post("/all")
async def all(request: Request):
    users = await User.all()
    return {"success": True, "message": "获取成功", "data": users}


@router.post("/list", response_model=DataList[UserPydantic])
async def list(params: Params = Depends()):
    users = await paginate(User.all().order_by("-id"), params)
    result = DataList[UserPydantic](success=True, message="获取成功", data=users)
    return result
