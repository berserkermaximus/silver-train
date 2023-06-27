from fastapi import FastAPI
from .schema import Identify
from .crud import identify, delete_all, delete
api = FastAPI()


@api.get("/", tags=['system'])
async def index():
    return "Hello World"


api.post("/identify", response_model=Identify)(identify)
api.post("/delete-all")(delete_all)
api.post("/delete")(delete)
