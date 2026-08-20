from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app.api.main import router

app = FastAPI()

app.include_router(router)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
