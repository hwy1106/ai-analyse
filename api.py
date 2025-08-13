from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os
import re
import uuid
import asyncio
from datetime import datetime
import json
from pathlib import Path

# Import your existing analysis functions
from analyse import read_statement, calculate_ratios, analyze_statement, StatementState

# Initialize FastAPI app
app = FastAPI(
    title="Financial Statement Analysis API",
    description="AI-powered financial statement analysis using LangGraph and Google Gemini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class AnalysisRequest(BaseModel):
    file_path: Optional[str] = Field(None, description="Path to existing PDF file")
    analysis_type: str = Field("full", description="Type of analysis: 'metrics', 'ratios', 'full'")

class AnalysisResponse(BaseModel):
    request_id: str
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str
    processing_time: Optional[float] = None

class AnalysisResult(BaseModel):
    request_id: str
    status: str
    metrics: Dict[str, float]
    ratios: Dict[str, str]
    analysis: str
    text_length: int
    timestamp: str
    processing_time: float

# Storage for analysis results (in production, use a proper database)
analysis_results: Dict[str, AnalysisResult] = {}
analysis_queue: Dict[str, Dict[str, Any]] = {}

# Utility functions
def save_uploaded_file(upload_file: UploadFile) -> str:
    """Save uploaded file and return the file path"""
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    # Generate unique filename
    file_extension = Path(upload_file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = upload_file.file.read()
        buffer.write(content)
    
    return str(file_path)

def cleanup_file(file_path: str):
    """Remove temporary file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ Cleaned up temporary file: {file_path}")
    except Exception as e:
        print(f"⚠️  Warning: Could not clean up file {file_path}: {e}")

async def process_analysis(request_id: str, file_path: str, analysis_type: str):
    """Background task to process the analysis"""
    start_time = datetime.now()
    
    try:
        # Update status to processing
        analysis_queue[request_id]["status"] = "processing"
        
        # Create initial state
        state = StatementState(
            file_path=file_path,
            text="",
            metrics={},
            ratios={},
            analysis=""
        )
        
        # Execute analysis pipeline
        if analysis_type in ["metrics", "full"]:
            state = read_statement(state)
        
        if analysis_type in ["ratios", "full"] and state["metrics"]:
            state = calculate_ratios(state)
        
        if analysis_type == "full" and state["metrics"] and state["ratios"]:
            state = analyze_statement(state)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Create result
        result = AnalysisResult(
            request_id=request_id,
            status="completed",
            metrics=state["metrics"],
            ratios=state["ratios"],
            analysis=state["analysis"],
            text_length=len(state["text"]),
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time
        )
        
        # Store result
        analysis_results[request_id] = result
        analysis_queue[request_id]["status"] = "completed"
        
        # Cleanup temporary file
        cleanup_file(file_path)
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        error_result = AnalysisResult(
            request_id=request_id,
            status="failed",
            metrics={},
            ratios={},
            analysis=f"Analysis failed: {str(e)}",
            text_length=0,
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time
        )
        analysis_results[request_id] = error_result
        analysis_queue[request_id]["status"] = "failed"
        analysis_queue[request_id]["error"] = str(e)

# API Endpoints
@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Financial Statement Analysis API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_key_configured": bool(os.getenv("GOO_API_KEY"))
    }

@app.post("/analyze/upload", response_model=AnalysisResponse)
async def analyze_upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF file to analyze"),
    analysis_type: str = "full"
):
    """Upload and analyze a PDF file"""
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Validate analysis type
    if analysis_type not in ["metrics", "ratios", "full"]:
        raise HTTPException(status_code=400, detail="Invalid analysis_type. Use 'metrics', 'ratios', or 'full'")
    
    # Check API key
    if not os.getenv("GOOGLE_API_KEY") and analysis_type == "full":
        raise HTTPException(status_code=500, detail="Google API key not configured")
    
    try:
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Save uploaded file
        file_path = save_uploaded_file(file)
        
        # Initialize queue entry
        analysis_queue[request_id] = {
            "status": "queued",
            "file_path": file_path,
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat()
        }
        
        # Start background processing
        background_tasks.add_task(process_analysis, request_id, file_path, analysis_type)
        
        return AnalysisResponse(
            request_id=request_id,
            status="queued",
            message="Analysis started successfully",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process upload: {str(e)}")

@app.post("/analyze/file", response_model=AnalysisResponse)
async def analyze_existing_file(
    background_tasks: BackgroundTasks,
    request: AnalysisRequest
):
    """Analyze an existing PDF file"""
    
    if not request.file_path:
        raise HTTPException(status_code=400, detail="file_path is required")
    
    if not os.path.exists(request.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check API key
    if not os.getenv("GOOGLE_API_KEY") and request.analysis_type == "full":
        raise HTTPException(status_code=500, detail="Google API key not configured")
    
    try:
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Initialize queue entry
        analysis_queue[request_id] = {
            "status": "queued",
            "file_path": request.file_path,
            "analysis_type": request.analysis_type,
            "timestamp": datetime.now().isoformat()
        }
        
        # Start background processing
        background_tasks.add_task(process_analysis, request_id, request.file_path, request.analysis_type)
        
        return AnalysisResponse(
            request_id=request_id,
            status="queued",
            message="Analysis started successfully",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")

@app.get("/status/{request_id}", response_model=Dict[str, Any])
async def get_analysis_status(request_id: str):
    """Get the status of an analysis request"""
    
    if request_id not in analysis_queue:
        raise HTTPException(status_code=404, detail="Request ID not found")
    
    queue_info = analysis_queue[request_id]
    
    # Check if analysis is complete
    if queue_info["status"] == "completed" and request_id in analysis_results:
        result = analysis_results[request_id]
        return {
            "request_id": request_id,
            "status": "completed",
            "result": result.dict(),
            "queue_info": queue_info
        }
    
    return {
        "request_id": request_id,
        "status": queue_info["status"],
        "queue_info": queue_info
    }

@app.get("/results/{request_id}", response_model=AnalysisResult)
async def get_analysis_results(request_id: str):
    """Get the completed analysis results"""
    
    if request_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis results not found")
    
    result = analysis_results[request_id]
    
    if result.status == "failed":
        raise HTTPException(status_code=500, detail=f"Analysis failed: {result.analysis}")
    
    return result

@app.get("/queue", response_model=Dict[str, Any])
async def get_queue_status():
    """Get the current analysis queue status"""
    return {
        "total_requests": len(analysis_queue),
        "completed": len([r for r in analysis_queue.values() if r["status"] == "completed"]),
        "processing": len([r for r in analysis_queue.values() if r["status"] == "processing"]),
        "queued": len([r for r in analysis_queue.values() if r["status"] == "queued"]),
        "failed": len([r for r in analysis_queue.values() if r["status"] == "failed"]),
        "requests": analysis_queue
    }

@app.delete("/cleanup/{request_id}")
async def cleanup_analysis(request_id: str):
    """Clean up analysis results and queue entry"""
    
    if request_id in analysis_results:
        del analysis_results[request_id]
    
    if request_id in analysis_queue:
        # Clean up temporary file if it exists
        queue_info = analysis_queue[request_id]
        if "file_path" in queue_info:
            cleanup_file(queue_info["file_path"])
        del analysis_queue[request_id]
    
    return {"message": f"Cleaned up analysis {request_id}"}

@app.delete("/cleanup/all")
async def cleanup_all():
    """Clean up all analysis results and queue entries"""
    
    # Clean up all temporary files
    for queue_info in analysis_queue.values():
        if "file_path" in queue_info:
            cleanup_file(queue_info["file_path"])
    
    # Clear all data
    analysis_results.clear()
    analysis_queue.clear()
    
    return {"message": "Cleaned up all analyses"}

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Create uploads directory
    Path("uploads").mkdir(exist_ok=True)
    
    print("🚀 Starting Financial Statement Analysis API...")
    print("📚 API Documentation available at: http://localhost:8000/docs")
    print("🔍 Alternative docs at: http://localhost:8000/redoc")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
