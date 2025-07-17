from fastapi import FastAPI
from contextlib import asynccontextmanager
from utils.logger import get_logger
import nltk

logger = get_logger("lifespan")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Starting AI Generation API (lifespan)", service="ai-gen-api", version="1.0.0")
    try:
        nltk.download('punkt')
        logger.info("NLTK punkt tokenizer downloaded successfully")
    except Exception as e:
        logger.error("Failed to download NLTK punkt", error=str(e))
    yield
    # Shutdown logic
    logger.info("Shutting down AI Generation API (lifespan)") 