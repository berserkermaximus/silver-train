from fastapi import FastAPI

api = FastAPI()


@api.get("/", tags=['system'])
async def index():
    return "Hello World"
