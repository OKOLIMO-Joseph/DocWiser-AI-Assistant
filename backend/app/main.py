from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any
import os
import sys

# Add the app directory to path to ensure imports work
sys.path.insert(0, os.path.dirname(__file__))

# Now import using absolute paths
from document_parser import DocumentParser
from llm_service import LLMService

app = FastAPI(
    title="DocWiser AI Assistant",
    description="AI-powered document analysis with Google Gemini",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini service
try:
    llm_service = LLMService()
    print(f" Gemini LLM Service initialized successfully")
    print(f"   Model: {llm_service.model_name}")
except Exception as e:
    print(f" Failed to initialize LLM Service: {str(e)}")
    llm_service = None

@app.get("/")
async def root():
    return {
        "message": "DocWiser API is running",
        "status": "active",
        "llm_provider": "Google Gemini" if llm_service else "Not initialized",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    gemini_status = "unknown"
    
    if llm_service:
        try:
            gemini_status = "connected" if llm_service.test_connection() else "connection_failed"
        except:
            gemini_status = "error"
    else:
        gemini_status = "not_initialized"
    
    return {
        "status": "healthy",
        "llm_provider": "google-gemini",
        "gemini_status": gemini_status,
        "api_ready": llm_service is not None
    }

@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload and analyze a document with Gemini AI"""
    
    if not llm_service:
        raise HTTPException(
            status_code=503,
            detail="AI service is not available. Please check server configuration."
        )
    
    try:
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.pdf', '.docx', '.doc']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Please upload PDF or DOCX files. Received: {file_extension}"
            )
        
        # Read file content
        content = await file.read()
        
        # Check file size
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB"
            )
        
        # Extract text
        try:
            extracted_text = DocumentParser.extract_text(content, file_extension)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract text: {str(e)}"
            )
        
        # Check if text was extracted
        if len(extracted_text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient text. The file may be empty or contain only images."
            )
        
        # Analyze with Gemini
        try:
            analysis = llm_service.analyze_document(extracted_text)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"AI analysis failed: {str(e)}"
            )
        
        # Return results
        return {
            "success": True,
            "filename": file.filename,
            "analysis": {
                "title": analysis.get("title", "Not detected"),
                "author": analysis.get("author", "Unknown"),
                "summary": analysis.get("summary", "No summary available")
            },
            "metadata": {
                "text_length": len(extracted_text),
                "file_size_bytes": len(content),
                "file_type": file_extension,
                "llm_provider": "google-gemini"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )