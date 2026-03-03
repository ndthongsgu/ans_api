from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.admin import router as admin_router
from api.v1.owner import router as owner_router
from api.v1.customer import router as customer_router
from core.database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# enable CORS so browser preflights succeed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust as needed in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router, prefix="/admin")
app.include_router(owner_router, prefix="/owner")
app.include_router(customer_router, prefix="/customer")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
