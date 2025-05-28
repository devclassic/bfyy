from fastapi import APIRouter
from models import User

router = APIRouter()


@router.get("/init")
async def init():
    admin = await User.get_or_none(username="root", is_admin=True)
    if not admin:
        await User.create(username="root", password="ddkjqwer", is_admin=True)
    return "系统初始化成功"
