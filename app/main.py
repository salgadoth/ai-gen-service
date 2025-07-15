from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routes.inference import router
import nltk
from utils.logger import get_logger
import time
import uuid

# Initialize logger
logger = get_logger("main")

app = FastAPI(
    title="AI Generation API",
    description="A FastAPI-based microservice for grammar correction and content insights",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")

# Download NLTK data
try:
    nltk.download('punkt')
    logger.info("NLTK punkt tokenizer downloaded successfully")
except Exception as e:
    logger.error("Failed to download NLTK punkt", error=str(e))

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting AI Generation API", 
               service="ai-gen-api", 
               version="1.0.0")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down AI Generation API")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all HTTP requests with structured logging"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # Log request
    logger.info("HTTP request received",
               request_id=request_id,
               method=request.method,
               url=str(request.url),
               client_ip=request.client.host if request.client else None,
               user_agent=request.headers.get("user-agent"))
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log successful response
        logger.info("HTTP request completed",
                   request_id=request_id,
                   status_code=response.status_code,
                   process_time=round(process_time, 4))
        
        return response
        
    except Exception as e:
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log error
        logger.error("HTTP request failed",
                    request_id=request_id,
                    error=str(e),
                    process_time=round(process_time, 4))
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {"status": "healthy", "service": "t5-grammar-api"}

if __name__ == '__main__':
    import uvicorn
    logger.info("Starting server with uvicorn", host="0.0.0.0", port=8000)
    uvicorn.run(app, host='0.0.0.0', port=8000) 