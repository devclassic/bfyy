from fastapi import APIRouter, Request, Depends
from fastapi_pagination import Params
from fastapi_pagination.ext.tortoise import paginate
from fastapi.responses import StreamingResponse
from models import History
from dtos.common import DataList, HistoryPydantic
import pandas as pd
import io

router = APIRouter(prefix="/history")


@router.post("/remove")
async def remove(request: Request):
    data = await request.json()
    history = await History.get_or_none(id=data["id"])
    if not history:
        return {"success": False, "message": "应用不存在"}
    await history.delete()
    return {"success": True, "message": "删除成功"}


@router.post("/remove_batch")
async def remove_batch(request: Request):
    data = await request.json()
    await History.filter(id__in=data["ids"]).delete()
    return {"success": True, "message": "删除成功"}


@router.post("/get")
async def get(request: Request):
    data = await request.json()
    history = await History.get_or_none(id=data["id"]).select_related("account", "app")
    if not history:
        return {"success": False, "message": "应用不存在"}
    return {"success": True, "message": "获取成功", "data": history}


@router.post("/list", response_model=DataList[HistoryPydantic])
async def list(params: Params = Depends()):
    historys = await paginate(
        History.all().select_related("account", "app").order_by("-id"), params
    )
    result = DataList[HistoryPydantic](success=True, message="获取成功", data=historys)
    return result


@router.get("/export")
async def export():
    historys = await History.all().select_related("account", "app").order_by("-id")
    data = {
        "账户": [],
        "应用": [],
        "提问时间": [],
        "问题": [],
        "回答时间": [],
        "回答": [],
    }
    for history in historys:
        data["账户"].append(history.account.name)
        data["应用"].append(history.app.name)
        data["提问时间"].append(history.question_time.strftime("%Y-%m-%d %H:%M:%S"))
        data["问题"].append(history.question)
        data["回答时间"].append(history.answer_time.strftime("%Y-%m-%d %H:%M:%S"))
        data["回答"].append(history.answer)
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    excel_bytes = buffer.getvalue()
    headers = {
        "Content-Disposition": f"attachment; filename={"问答历史数据".encode("utf-8").decode("latin1")}.xlsx"
    }
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return StreamingResponse(
        io.BytesIO(excel_bytes), media_type=media_type, headers=headers
    )
