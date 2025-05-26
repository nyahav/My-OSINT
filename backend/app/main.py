import secrets
import time
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.config import app_description, app_name, app_title, app_version, settings
from app.routers import auth
from app.routers.domain import domain as scan

from dotenv import load_dotenv

# Import the init_db function from your database session module
# Assuming it's in app/db/session.py and named init_db
from app.db.session import init_db # <--- ADD THIS LINE
load_dotenv()
app = FastAPI(
    title=app_title,
    description=app_description,
    version=app_version,
    docs_url="/",
    root_path=settings.root_path,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:3001",
        "http://localhost:3001",
    ],
)

# Session Middleware
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(16))

# Custom Audit Middleware
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = str(round(time.time() - start_time, 3))
    response.headers["X-Process-Time"] = process_time
    return response

# Include Routers
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    scan.router,
    prefix="/scan",
    tags=["scan"],
)

# --- NEW: Database Initialization on Startup ---
@app.on_event("startup")
async def on_startup():
    """
    Event handler that runs when the FastAPI application starts up.
    It calls the init_db function to ensure database tables are created.
    """
    print("Application startup: Initializing database...")
    await init_db()
    print("Database initialization complete.")
# --- END NEW ---


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="debug",
        reload=True,
    )