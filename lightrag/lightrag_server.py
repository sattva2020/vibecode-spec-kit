from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from typing import List, Dict, Any
import json

app = FastAPI(title="LightRAG API", version="1.0.0")

# LightRAG imports
try:
    from lightrag import LightRAG, QueryParam
    from lightrag.llm.ollama import ollama_model_complete, ollama_embed
    from lightrag.utils import EmbeddingFunc
    from lightrag.kg.shared_storage import initialize_pipeline_status
    LIGHTRAG_AVAILABLE = True
except ImportError:
    LIGHTRAG_AVAILABLE = False
    print("LightRAG not available, using mock implementation")

# Configuration
WORKING_DIR = os.getenv("LIGHTRAG_WORKING_DIR", "/app/data")
LLM_MODEL = os.getenv("LIGHTRAG_LLM_MODEL", "qwen2.5-coder:7b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-m3:latest")

# Initialize LightRAG if available
rag = None

async def initialize_lightrag():
    global rag
    if not LIGHTRAG_AVAILABLE:
        return False
    
    try:
        rag = LightRAG(
            working_dir=WORKING_DIR,
            llm_model_func=ollama_model_complete,
            llm_model_name=LLM_MODEL,
            llm_model_kwargs={
                "host": OLLAMA_HOST,
                "options": {"num_ctx": 8192},
                "timeout": 300,
            },
            embedding_func=EmbeddingFunc(
                embedding_dim=1024,
                max_token_size=8192,
                func=lambda texts: ollama_embed(
                    texts,
                    embed_model=EMBEDDING_MODEL,
                    host=OLLAMA_HOST,
                ),
            ),
        )
        
        await rag.initialize_storages()
        await initialize_pipeline_status()
        print(f"LightRAG initialized with working_dir: {WORKING_DIR}")
        return True
    except Exception as e:
        print(f"Failed to initialize LightRAG: {e}")
        return False

class InsertRequest(BaseModel):
    text: str
    metadata: Dict[str, Any] = {}

class QueryRequest(BaseModel):
    text: str
    mode: str = "hybrid"  # global, local, hybrid
    param: Dict[str, Any] = {}

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]] = []

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "LightRAG API",
        "lightrag_available": LIGHTRAG_AVAILABLE,
        "working_dir": WORKING_DIR
    }

@app.post("/api/insert")
async def insert_text(request: InsertRequest):
    """Insert text into LightRAG knowledge base"""
    if not LIGHTRAG_AVAILABLE or rag is None:
        raise HTTPException(status_code=503, detail="LightRAG not available")
    
    try:
        result = await rag.ainsert(request.text)
        return {
            "status": "success",
            "message": "Text inserted successfully",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insert failed: {str(e)}")

@app.post("/api/query", response_model=QueryResponse)
async def query_knowledge(request: QueryRequest):
    """Query LightRAG knowledge base"""
    if not LIGHTRAG_AVAILABLE or rag is None:
        # Mock response for testing
        return QueryResponse(
            answer=f"Mock response for query: {request.text}",
            sources=[{"title": "Mock Source", "content": request.text}]
        )
    
    try:
        # Create QueryParam
        param = QueryParam(
            mode=request.mode,
            **request.param
        )
        
        result = await rag.aquery(request.text, param)
        
        return QueryResponse(
            answer=result,
            sources=[]  # LightRAG doesn't return sources by default
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """Get LightRAG statistics"""
    if not LIGHTRAG_AVAILABLE:
        return {
            "status": "mock",
            "lightrag_available": False
        }
    
    try:
        # Get basic stats from working directory
        stats = {
            "working_dir": WORKING_DIR,
            "lightrag_available": True,
            "files_count": 0
        }
        
        if os.path.exists(WORKING_DIR):
            stats["files_count"] = len(os.listdir(WORKING_DIR))
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize LightRAG on startup"""
    await initialize_lightrag()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup LightRAG on shutdown"""
    global rag
    if rag is not None:
        await rag.finalize_storages()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
