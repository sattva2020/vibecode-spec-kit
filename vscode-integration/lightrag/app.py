from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from lightrag import LightRAG, QueryParam
import asyncio
import os
from typing import Optional, List
import uvicorn

app = FastAPI(title="LightRAG API for VS Code Integration")

# CORS для VS Code extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация LightRAG
WORKING_DIR = os.getenv("WORKING_DIR", "./working_dir")

rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=lambda x: f"Processed: {x}",  # Placeholder for Ollama integration
    embedding_func=lambda x: [0.1] * 1536,  # Placeholder for embeddings
)


class InsertRequest(BaseModel):
    text: str
    description: Optional[str] = None
    source: Optional[str] = None


class QueryRequest(BaseModel):
    query: str
    mode: str = "hybrid"  # naive, local, global, hybrid
    top_k: int = 10


class BatchInsertRequest(BaseModel):
    texts: List[str]
    source: Optional[str] = None


class CodeContextRequest(BaseModel):
    file_path: str
    code: str
    language: str
    context: Optional[dict] = None


@app.post("/insert")
async def insert_document(request: InsertRequest):
    """Добавить документ в RAG"""
    try:
        await asyncio.to_thread(rag.insert, request.text)
        return {
            "status": "success",
            "message": "Document inserted",
            "source": request.source,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/insert_code")
async def insert_code(request: CodeContextRequest):
    """Добавить код с контекстом в RAG"""
    try:
        # Формируем контекстный текст для RAG
        context_text = f"""
File: {request.file_path}
Language: {request.language}

Code:
{request.code}

Context: {request.context or "No additional context"}
"""
        await asyncio.to_thread(rag.insert, context_text)
        return {
            "status": "success",
            "message": "Code inserted with context",
            "file_path": request.file_path,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/insert_batch")
async def insert_batch(request: BatchInsertRequest):
    """Добавить несколько документов"""
    try:
        for i, text in enumerate(request.texts):
            await asyncio.to_thread(rag.insert, text)
        return {
            "status": "success",
            "message": f"{len(request.texts)} documents inserted",
            "source": request.source,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query_rag(request: QueryRequest):
    """Выполнить запрос к RAG"""
    try:
        result = await asyncio.to_thread(
            rag.query,
            request.query,
            param=QueryParam(mode=request.mode, top_k=request.top_k),
        )
        return {"result": result, "query": request.query, "mode": request.mode}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/suggest")
async def suggest_code(request: Request):
    """Предложить код на основе контекста"""
    try:
        data = await request.json()
        context = data.get("context", "")
        cursor_position = data.get("cursor_position", {})

        # Простой пример предложения
        suggestion = {
            "text": "// AI suggestion based on context",
            "confidence": 0.8,
            "type": "completion",
        }

        return {"suggestions": [suggestion], "context": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "lightrag", "working_dir": WORKING_DIR}


@app.get("/stats")
async def get_stats():
    """Получить статистику RAG"""
    try:
        # Простая статистика
        return {
            "documents_indexed": 100,  # Placeholder
            "working_dir": WORKING_DIR,
            "status": "operational",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
