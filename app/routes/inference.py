import os
from fastapi import APIRouter, HTTPException
from models.grammar_corrector import GrammarCorrector
from schemas.prompt import Prompt

router = APIRouter()
model = GrammarCorrector()

@router.post("/inference")
async def infer(prompt: Prompt):
    try:
        errors = model.infer(prompt.text)
        return {"corrected": errors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))