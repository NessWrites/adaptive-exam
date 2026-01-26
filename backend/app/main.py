from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import exam_route
from backend.app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Adaptive Exam API",
    description="2D MIRT Computerized Adaptive Testing System",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(exam_route.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Adaptive Exam API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )