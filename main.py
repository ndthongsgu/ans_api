from fastapi import FastAPI
from api.v1.users import router as user_router
from api.v1.areas import router as area_router
from api.v1.staffs import router as staff_router
from api.v1.stalls import router as stall_router
from api.v1.stall_contents import router as stall_content_router
from api.v1.roles import router as role_router
from api.v1.user_roles import router as user_role_router
from api.v1.customers import router as customer_router
from api.v1.employees import router as employee_router
from api.v1.listening_histories import router as listening_history_router
from core.database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_router)
app.include_router(area_router)
app.include_router(staff_router)
app.include_router(stall_router)
app.include_router(stall_content_router)
app.include_router(role_router)
app.include_router(user_role_router)
app.include_router(customer_router)
app.include_router(employee_router)
app.include_router(listening_history_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
