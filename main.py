from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json
from typing import Any

# Import logging config first
import logging_config

from api.v1.admin import router as admin_router
from api.v1.owner import router as owner_router
from api.v1.mobile import router as mobile_router
from modules.actionLog.controllers.admin_controller import router as action_log_router
from core.database import engine, Base
from common.dto.response import error_response

# Custom JSON encoder for UTF-8 support
class UTF8JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that ensures UTF-8 encoding"""
    def encode(self, o: Any) -> str:
        # Use ensure_ascii=False to preserve Unicode characters
        return super().encode(o)

# Custom JSON response class for UTF-8
class UTF8JSONResponse(JSONResponse):
    """JSON response that ensures UTF-8 encoding"""
    def render(self, content: Any) -> bytes:
        # Use json.dumps with ensure_ascii=False
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(',', ':')
        ).encode('utf-8')

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ANS API",
    version="1.0.0",
    default_response_class=UTF8JSONResponse,
)

# enable CORS so browser preflights succeed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust as needed in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware to ensure UTF-8 JSON encoding
@app.middleware("http")
async def set_utf8_header(request, call_next):
    response = await call_next(request)
    if "application/json" in response.headers.get("content-type", ""):
        response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

app.include_router(admin_router, prefix="/admin")
app.include_router(owner_router, prefix="/owner")
app.include_router(mobile_router, prefix="/mobile")
app.include_router(action_log_router)

# Serve audio files
audios_dir = Path(__file__).parent / "audios"
audios_dir.mkdir(exist_ok=True)
app.mount("/audios", StaticFiles(directory=str(audios_dir)), name="audios")

# Serve stall images
images_dir = Path(__file__).parent / "stallImages"
images_dir.mkdir(exist_ok=True)
app.mount("/stallImages", StaticFiles(directory=str(images_dir)), name="stallImages")

# Global exception handler for HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return UTF8JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=exc.detail,
            error=exc.detail,
            status_code=exc.status_code
        ),
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
