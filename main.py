from fastapi import FastAPI
from api.v1.users import router as user_router
from core.database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
