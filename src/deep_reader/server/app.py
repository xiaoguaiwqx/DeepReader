from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from deep_reader.storage.db_manager import DatabaseManager
from deep_reader.models import Paper
from deep_reader.core_loop import run_daily_cycle

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

class TriggerRequest(BaseModel):
    category: str = "cs.AI OR cs.LG OR cs.CV OR cs.CL"
    days: Optional[int] = None
    topic: Optional[str] = None
    query: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

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

@app.post("/api/trigger", tags=["Jobs"])
async def trigger_fetch(request: TriggerRequest, background_tasks: BackgroundTasks):
    """
    Manually trigger the fetch cycle in the background.
    """
    if request.query:
        background_tasks.add_task(run_daily_cycle, query=request.query)
        message = f"Fetch job triggered with custom query: {request.query}"
    else:
        background_tasks.add_task(
            run_daily_cycle, 
            category=request.category, 
            days=request.days, 
            topic=request.topic,
            start_date_str=request.start_date,
            end_date_str=request.end_date
        )
        msg_parts = [f"category: {request.category}"]
        if request.start_date and request.end_date:
            msg_parts.append(f"range: {request.start_date} to {request.end_date}")
        elif request.days:
            msg_parts.append(f"last {request.days} days")
        
        if request.topic:
            msg_parts.append(f"topic: {request.topic}")
            
        message = f"Fetch job triggered for {', '.join(msg_parts)}"
        
    return {"status": "accepted", "message": message}
