import os
from fastapi import APIRouter, HTTPException
from models.t5_model import T5Model
from utils.tokenizer import tokenize_input
from schemas.prompt import Prompt

MODEL_DIR = "./app/trainer/t5-trained"
router = APIRouter()

if os.path.exists(MODEL_DIR):
    model_ready = True
    model = T5Model(model_path=MODEL_DIR)
else:
    model_ready = False

@router.post("/inference")
async def infer(prompt: Prompt):
    if not model_ready:
        return {"detail": "Model is training. Please try again later."}
    else: 
        try:
            tokenized_input = tokenize_input(prompt.text)
            errors = model.predict(tokenized_input)
            return {"grammar_errors": errors}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))