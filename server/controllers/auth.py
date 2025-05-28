from fastapi import APIRouter, Request
from models import User
from uuid import uuid4

router = APIRouter(prefix="/auth")


@router.post("/login")
async def login(request: Request):
    data = await request.json()
    user = await User.get_or_none(**data, is_admin=True)
    if not user:
        return {"success": False, "message": "用户名或密码错误"}
    else:
        token = uuid4()
        user.token = str(token)
        await user.save(update_fields=["token"])
        return {"success": True, "message": "登录成功", "token": token}


@router.post("/check")
async def logout(request: Request):
    token = request.headers.get("token")
    if not token:
        return {"success": False, "message": "尚未登录"}
    user = await User.get_or_none(token=token)
    if user:
        return {"success": True, "message": "已登录"}
    else:
        return {"success": False, "message": "尚未登录"}
