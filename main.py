from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Import logging config first
import logging_config

from api.v1.admin import router as admin_router
from api.v1.owner import router as owner_router
from api.v1.mobile import router as mobile_router
from modules.actionLog.controllers.admin_controller import router as action_log_router
from core.database import engine, Base
from common.dto.response import error_response

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
app.include_router(mobile_router, prefix="/mobile")
app.include_router(action_log_router)

# Serve audio files
audios_dir = Path(__file__).parent / "audios"
audios_dir.mkdir(exist_ok=True)
app.mount("/audios", StaticFiles(directory=str(audios_dir)), name="audios")

# Global exception handler for HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=exc.detail,
            error=exc.detail,
            status_code=exc.status_code
        )
    )

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
