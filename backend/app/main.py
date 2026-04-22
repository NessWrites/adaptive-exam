from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import exam_route
from backend.app.core.config import get_settings
from generator.question_gen_system.routes import routes
from generator.mcq_generator.api.routes import router as mcq_generator_router 
from backend.app.core.logging import setup_logging

settings = get_settings()
logger = setup_logging("adaptive_exam_api")

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
app.include_router(routes.router, prefix="/questions", tags= ['Question Generator'])
app.include_router(mcq_generator_router)

@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Accessing root endpoint")
    return {
        "message": "Adaptive Exam API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
