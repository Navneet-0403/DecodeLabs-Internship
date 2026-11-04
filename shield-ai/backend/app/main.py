import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from .database import init_db, check_db_health
from .exceptions import APIException, api_exception_handler, validation_exception_handler, general_exception_handler
from .schemas.common import HealthResponse

from .routes import (
    dashboard,
    scanner,
    agents,
    tool_catalog,
    permissions,
    approvals,
    events,
    simulator,
    settings,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and run migrations/seeds safely
    init_db()
    yield

app = FastAPI(
    title="Shield AI — AI Agent Security Shield",
    description="Relational Database Integration & Policy Interceptor for Shield AI (DecodeLabs Project 3)",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Exception handlers for standard Gatekeeper error contract
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# CORS configuration for local development and cross-origin frontend setups
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8080",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health endpoint accurately reflecting database availability
@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    is_db_connected = check_db_health()
    db_status = "connected" if is_db_connected else "disconnected"
    overall_status = "ok" if is_db_connected else "error"
    return HealthResponse(
        status=overall_status,
        application="Shield AI",
        api_version="1.0.0",
        database=db_status
    )

# Include API Routers
app.include_router(dashboard.router)
app.include_router(scanner.router)
app.include_router(agents.router)
app.include_router(tool_catalog.router)
app.include_router(permissions.router)
app.include_router(approvals.router)
app.include_router(events.router)
app.include_router(simulator.router)
app.include_router(settings.router)
app.include_router(settings.demo_router)

# Static file serving and Frontend integration
css_dir = BASE_DIR / "css"
js_dir = BASE_DIR / "js"
assets_dir = BASE_DIR / "assets"
screenshots_dir = BASE_DIR / "screenshots"

if css_dir.is_dir():
    app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
if js_dir.is_dir():
    app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")
if assets_dir.is_dir():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
if screenshots_dir.is_dir():
    app.mount("/screenshots", StaticFiles(directory=str(screenshots_dir)), name="screenshots")

@app.get("/", include_in_schema=False)
async def serve_index():
    index_file = BASE_DIR / "index.html"
    return FileResponse(index_file)
