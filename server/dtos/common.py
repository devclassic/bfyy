from pydantic import BaseModel
from fastapi_pagination import Page
from tortoise.contrib.pydantic import pydantic_model_creator
from models import App, Account, User, History


class DataList[dt](BaseModel):
    success: bool
    message: str
    data: Page[dt]


AppPydantic = pydantic_model_creator(App, name="App")
AccountPydantic = pydantic_model_creator(Account, name="Account")
UserPydantic = pydantic_model_creator(User, name="User")


class HistoryPydantic(pydantic_model_creator(History, name="History")):
    account: AccountPydantic
    app: AppPydantic
