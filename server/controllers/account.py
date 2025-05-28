from fastapi import APIRouter, Request, Depends
from models import Account
from fastapi_pagination import Params
from fastapi_pagination.ext.tortoise import paginate
from dtos.common import DataList, AccountPydantic

router = APIRouter(prefix="/account")


@router.post("/add")
async def add(request: Request):
    data = await request.json()
    account = await Account.create(**data)
    return {"success": True, "message": "添加成功", "data": account}


@router.post("/remove")
async def remove(request: Request):
    data = await request.json()
    account = await Account.get_or_none(id=data["id"])
    if not account:
        return {"success": False, "message": "应用不存在"}
    await account.delete()
    return {"success": True, "message": "删除成功"}


@router.post("/remove_batch")
async def remove_batch(request: Request):
    data = await request.json()
    await Account.filter(id__in=data["ids"]).delete()
    return {"success": True, "message": "删除成功"}


@router.post("/update")
async def update(request: Request):
    data = await request.json()
    account = await Account.get_or_none(id=data["id"])
    if not account:
        return {"success": False, "message": "账户不存在"}
    await account.update_from_dict(data)
    del data["id"]
    await account.save(update_fields=data.keys())
    return {"success": True, "message": "更新成功"}


@router.post("/get")
async def get(request: Request):
    data = await request.json()
    account = await Account.get_or_none(id=data["id"])
    if not account:
        return {"success": False, "message": "账户不存在"}
    return {"success": True, "message": "获取成功", "data": account}


@router.post("/list", response_model=DataList[AccountPydantic])
async def list(params: Params = Depends()):
    accounts = await paginate(Account.all().order_by("-id"), params)
    result = DataList[AccountPydantic](success=True, message="获取成功", data=accounts)
    return result
