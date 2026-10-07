from contextlib import asynccontextmanager
import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.ml.rag_engine import MultilingualRAGEngine
from app.ml.matcher import EligibilityMatcher
from app.services.ocr_service import DocumentOCRService

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=== Starting AI-Based Multilingual Government Assistant Backend ===")
    print(f"CUDA GPU Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU Device: {torch.cuda.get_device_name(0)}")
    
    # Warm up / initialize singletons
    print("[Startup] Initializing RAG Engine...")
    MultilingualRAGEngine.get_instance()

    print("[Startup] Initializing Neural Matcher...")
    EligibilityMatcher.get_instance()

    print("[Startup] Initializing OCR Service...")
    DocumentOCRService.get_instance()

    print("=== All AI models loaded and ready! ===")
    yield
    print("=== Shutting down Backend ===")

app = FastAPI(
    title="Multilingual Government Scheme & Job Assistant API",
    description="AI/ML backend using Neural Networks, OCR, RAG, and NLP to simplify schemes and match job notifications.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Streamlit / React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router)

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "service": "Multilingual Government Scheme & Job Assistant",
        "docs": "/docs",
        "gpu_accelerated": torch.cuda.is_available()
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
