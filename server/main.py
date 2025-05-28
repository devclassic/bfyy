from contextlib import asynccontextmanager
from tortoise.contrib.fastapi import RegisterTortoise
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config import TORTOISE_ORM
from controllers import routers
from models import User
from fastapi_pagination import add_pagination
import os
from fastapi.staticfiles import StaticFiles

upload_dir = "database"
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)


@asynccontextmanager
async def lifespan(app):
    async with RegisterTortoise(app, config=TORTOISE_ORM, generate_schemas=True):
        yield


app = FastAPI(
    title="AI应用管理后台",
    lifespan=lifespan,
)

app.mount("/ui", StaticFiles(directory="public/ui", html=True))
app.mount("/admin", StaticFiles(directory="public/admin", html=True))


@app.middleware("http")
async def auth(request: Request, call_next):
    path = request.url.path
    uncheck = [
        path.startswith("/init"),
        path.startswith("/auth"),
        path.startswith("/client"),
        path.startswith("/public"),
        path.startswith("/history/export"),
        path.startswith("/ui"),
        path.startswith("/admin"),
    ]
    if any(uncheck):
        return await call_next(request)

    token = request.headers.get("token")
    user = await User.get_or_none(token=token, is_admin=True)

    if not user:
        return JSONResponse(content={"success": False, "message": "尚未登陆"})
    else:
        return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

for router in routers:
    app.include_router(router)

add_pagination(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
