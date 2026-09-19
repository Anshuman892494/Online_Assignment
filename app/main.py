from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.config import settings
from app.core.database import init_db
from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.review import router as review_router
from app.api.v1.questions import router as questions_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database schemas
    await init_db()
    yield
    # Shutdown: cleanup if needed

app = FastAPI(
    title=settings.APP_NAME,
    description="""
## Pragati Bharati Engineering Assignment — Round 2
### Document Intelligence & Question Extraction Service

Production-grade asynchronous service for ingesting examination documents (PDF/Images), 
extracting structured questions with options, detecting answer keys, handling imperfect scans 
and cross-page continuations, and providing confidence-based review queues.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(review_router, prefix="/api/v1")
app.include_router(questions_router, prefix="/api/v1")

from fastapi.responses import FileResponse

# Mount static files
static_path = Path(__file__).resolve().parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@app.get("/", tags=["UI Dashboard"])
async def root_workbench():
    """Serves the Classic Retro Workbench UI."""
    index_file = static_path / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": f"Welcome to {settings.APP_NAME}. Explore /docs for API."}

from fastapi.responses import Response

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Silently handles browser favicon requests with 204 No Content."""
    return Response(status_code=204)

@app.get("/health", tags=["System"])
@app.get("/api/v1/health", tags=["System"])
async def health_check():
    """System liveness and readiness probe."""
    return {
        "status": "HEALTHY",
        "service": settings.APP_NAME,
        "environment": settings.ENVIRONMENT
    }
