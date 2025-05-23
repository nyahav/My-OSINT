import secrets
import time
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.routers.domain import domain
from app.config import app_description, app_name, app_title, app_version, settings
from app.routers import auth
# from app.routers.domain import domain  # Uncomment if you have domain router

app = FastAPI(
    title=app_title,
    description=app_description,
    version=app_version,
    docs_url="/",
    root_path=settings.root_path,
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
)

app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(16))

@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = str(round(time.time() - start_time, 3))
    response.headers["X-Process-Time"] = process_time
    return response

app.include_router(
    auth.router,
    prefix="/v1/auth",
    tags=["auth"],
)

app.include_router(
    domain.router,
    prefix="/v1/domain",
    tags=["domain"],
)

# app.include_router(
#     domain.router,
#     prefix="/v1/domain",
#     tags=["domain"],
# )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="debug",
        reload=True,
    )