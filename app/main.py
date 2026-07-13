import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1 import routes_analysis, routes_auth, routes_user, routes_waitlist, routes_analytics
from app.config import settings, run_startup_checks
from app.db.session import SessionLocal
from app.core.exceptions import (
    NotFoundException, BadRequestException, UnauthorizedException, RateLimitException
)

# ── Logging setup ────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("skinscan")

# ── App factory ──────────────────────────────────────────────
app = FastAPI(
    title="SkinScan API",
    version="1.0.0",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
)

# ── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:3000", "https://www.skinscan.fit"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ── Startup event ────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    run_startup_checks(settings)


# ── Request logging middleware ───────────────────────────────
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000)
    logger.info(
        f"{request.method} {request.url.path} → {response.status_code} ({duration_ms}ms)"
    )
    return response


# ── Security headers middleware ──────────────────────────────
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return response


# ── Exception handlers ───────────────────────────────────────
@app.exception_handler(NotFoundException)
async def not_found_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": "NOT_FOUND", "message": exc.detail}},
    )

@app.exception_handler(BadRequestException)
async def bad_request_handler(request: Request, exc: BadRequestException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": "BAD_REQUEST", "message": exc.detail}},
    )

@app.exception_handler(UnauthorizedException)
async def unauthorized_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": "UNAUTHORIZED", "message": exc.detail}},
    )

@app.exception_handler(RateLimitException)
async def rate_limit_handler(request: Request, exc: RateLimitException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": "RATE_LIMIT_EXCEEDED", "message": exc.detail}},
    )

@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception):
    if not settings.is_production:
        logger.exception(f"Unhandled error on {request.method} {request.url.path}")
    else:
        logger.error(f"Unhandled error on {request.method} {request.url.path}: {type(exc).__name__}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred."}},
    )


# ── Routes ───────────────────────────────────────────────────
app.include_router(routes_auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(routes_user.router, prefix="/api/v1", tags=["user"])
app.include_router(routes_analysis.router, prefix="/api/v1/analyze", tags=["analyze"])
app.include_router(routes_waitlist.router, prefix="/api/v1/waitlist", tags=["waitlist"])
app.include_router(routes_analytics.router, prefix="/api/v1/analytics", tags=["analytics"])


# ── Health check (verifies DB connectivity) ──────────────────
@app.get("/healthz")
def health_check():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ok", "db": "connected"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "db": "unreachable"},
        )
