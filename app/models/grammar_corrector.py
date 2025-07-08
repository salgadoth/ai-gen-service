from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from torch import torch

class GrammarCorrector:
    def __init__(self, model_name="deep-learning-analytics/GrammarCorrector"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)

    def infer(self, prompt, max_length=128):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            **inputs,
            max_length=max_length, 
            num_beams=4, 
            early_stopping=True
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)