import os
from fastapi import APIRouter, HTTPException, Depends, status
from models.grammar_corrector import GrammarCorrector
from schemas.prompt import Prompt, GrammarAnalysisResponse, InsightsResponse
from utils.split import split_into_sentences
from models.ollama_service import InsufficientContentError
from utils.logger import get_logger
import time

from utils.jwt import verify_jwt

# Initialize logger
logger = get_logger("inference")

router = APIRouter()
model = GrammarCorrector()

@router.post("/grammar", response_model=GrammarAnalysisResponse)
async def grammar_only(prompt: Prompt, user_claims: dict = Depends(verify_jwt)):
    """Grammar correction only endpoint"""
    start_time = time.time()
    
    logger.info("Grammar correction request received",
               text_length=len(prompt.text),
               include_explanations=prompt.include_explanations)
    
    try:
        result = model.analyse(
            original=prompt.text,
            include_explanations=prompt.include_explanations or False
        )
        
        process_time = time.time() - start_time
        logger.info("Grammar correction completed successfully",
                   process_time=round(process_time, 3),
                   sentence_count=len(result["sentences"]))
        
        return result
    except Exception as e:
        process_time = time.time() - start_time
        logger.error("Grammar correction failed",
                    error=str(e),
                    process_time=round(process_time, 3))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insights", response_model=InsightsResponse)
async def insights_only(prompt: Prompt, user_claims: dict = Depends(verify_jwt)):
    """Content insights only endpoint - uses original text as base rate"""
    start_time = time.time()
    
    logger.info("Content insights request received",
               text_length=len(prompt.text),
               has_full_context=prompt.full_context is not None)
    
    try:
        insights = model.ollama.generate_content_insights(
            text=prompt.text,
            full_context=prompt.full_context
        )
        
        process_time = time.time() - start_time
        logger.info("Content insights completed successfully",
                   process_time=round(process_time, 3),
                   insights_length=len(insights))
        
        return InsightsResponse(
            insights=insights,
            original=prompt.text
        )
    except InsufficientContentError as e:
        process_time = time.time() - start_time
        logger.warning("Content insights request rejected - insufficient content",
                      error=str(e),
                      process_time=round(process_time, 3))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        process_time = time.time() - start_time
        logger.error("Content insights failed",
                    error=str(e),
                    process_time=round(process_time, 3))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-base-rate")
async def check_base_rate(prompt: Prompt, user_claims: dict = Depends(verify_jwt)):
    """Check if content meets minimum requirements for insights analysis"""
    logger.debug("Base rate check request received",
                text_length=len(prompt.text),
                has_full_context=prompt.full_context is not None)
    
    try:
        meets_requirements = model.ollama._meets_threshold(
            prompt.full_context if prompt.full_context else prompt.text
        )
        
        if meets_requirements:
            sentences = split_into_sentences(
                prompt.full_context if prompt.full_context else prompt.text
            )
            word_count = len((prompt.full_context if prompt.full_context else prompt.text).split())
            
            logger.debug("Base rate check passed",
                        sentence_count=len(sentences),
                        word_count=word_count)
            
            return {
                "meets_base_rate": True,
                "sentence_count": len(sentences),
                "word_count": word_count,
                "min_sentences": model.ollama.min_sentences,
                "min_words": model.ollama.min_words
            }
        else:
            logger.debug("Base rate check failed",
                        min_sentences=model.ollama.min_sentences,
                        min_words=model.ollama.min_words)
            
            return {
                "meets_base_rate": False,
                "message": f"Need at least {model.ollama.min_sentences} sentences and {model.ollama.min_words} words for insights analysis"
            }
    except Exception as e:
        logger.error("Base rate check failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))