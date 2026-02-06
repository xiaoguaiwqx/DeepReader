from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv

from deep_reader.storage.db_manager import DatabaseManager
from deep_reader.models import Paper
from deep_reader.core_loop import run_daily_cycle
from deep_reader.server.job_store import JobStatus, create_job, get_job

# Load env vars
load_dotenv()

# Initialize DB Manager
db_manager = DatabaseManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure DB is ready (already handled by DatabaseManager init)
    print("Server starting...")
    yield
    # Shutdown
    print("Server shutting down...")

app = FastAPI(title="DeepReader API", version="0.2.0", lifespan=lifespan)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": "HTTP_ERROR",
            "message": str(exc.detail),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "code": "INVALID_PARAMS",
            "message": "Invalid request parameters.",
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "code": "INTERNAL_ERROR",
            "message": "Internal server error.",
        },
    )

# CORS (Allow Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev, allow all. Restrict in prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models for API ---
class PaperListResponse(BaseModel):
    items: List[Paper]
    total: int
    limit: int
    offset: int

class StatsResponse(BaseModel):
    total: int
    last_fetch_time: Optional[str] = None
    categories: Dict[str, int]
    with_summary: int
    without_summary: int

class CategoriesResponse(BaseModel):
    categories: List[str]

class TriggerRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    days: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    topic: Optional[str] = None
    max_results: int = 200

# --- Endpoints ---

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "DeepReader API is running"}

@app.get("/api/papers", response_model=PaperListResponse, tags=["Papers"])
async def get_papers(
    limit: int = 20,
    offset: int = 0,
    topic: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """
    Get a paginated list of papers.
    """
    papers = db_manager.get_recent_papers(
        limit=limit,
        offset=offset,
        topic=topic,
        start_date=start_date,
        end_date=end_date,
    )
    total = db_manager.count_papers_filtered(
        topic=topic,
        start_date=start_date,
        end_date=end_date,
    )
    
    return PaperListResponse(
        items=papers,
        total=total,
        limit=limit,
        offset=offset
    )

@app.get("/api/papers/{paper_id}", response_model=Paper, tags=["Papers"])
async def get_paper_detail(paper_id: str):
    """
    Get details of a specific paper.
    """
    paper = db_manager.get_paper(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper

@app.get("/api/stats", response_model=StatsResponse, tags=["Stats"])
async def get_stats():
    stats = db_manager.get_stats()
    return StatsResponse(**stats)

@app.get("/api/categories", response_model=CategoriesResponse, tags=["Stats"])
async def get_categories():
    categories = db_manager.get_categories()
    return CategoriesResponse(categories=categories)

@app.get("/api/jobs/{job_id}", response_model=JobStatus, tags=["Jobs"])
async def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.post("/api/trigger", tags=["Jobs"])
async def trigger_fetch(request: TriggerRequest, background_tasks: BackgroundTasks):
    """
    Manually trigger the fetch cycle in the background.
    """
    if not request.query and not request.category:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "code": "INVALID_PARAMS",
                "message": "category is required when query is not provided."
            }
        )
    if request.days is not None and (request.start_date or request.end_date):
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "code": "INVALID_PARAMS",
                "message": "days is mutually exclusive with start_date/end_date."
            }
        )
    if (request.start_date and not request.end_date) or (request.end_date and not request.start_date):
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "code": "INVALID_PARAMS",
                "message": "start_date and end_date must be provided together."
            }
        )

    job = create_job()
    if request.query:
        background_tasks.add_task(
            run_daily_cycle,
            query=request.query,
            max_results=request.max_results,
            job_id=job.job_id,
        )
        message = f"Fetch job triggered with custom query: {request.query}"
    else:
        background_tasks.add_task(
            run_daily_cycle, 
            category=request.category,
            days=request.days, 
            topic=request.topic,
            start_date_str=request.start_date,
            end_date_str=request.end_date,
            max_results=request.max_results,
            job_id=job.job_id
        )
        msg_parts = [f"category: {request.category}"]
        if request.start_date and request.end_date:
            msg_parts.append(f"range: {request.start_date} to {request.end_date}")
        elif request.days:
            msg_parts.append(f"last {request.days} days")
        
        if request.topic:
            msg_parts.append(f"topic: {request.topic}")
            
        message = f"Fetch job triggered for {', '.join(msg_parts)}"
        
    return {"status": "accepted", "job_id": job.job_id, "message": message}
