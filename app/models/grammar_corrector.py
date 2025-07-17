from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
from utils.diff import diff_original_with_corrected
from utils.split import split_into_sentences
from models.ollama_service import OllamaService
from utils.logger import get_logger
from typing import Optional
import time
import json


class GrammarCorrector:
    def __init__(self, model_name="deep-learning-analytics/GrammarCorrector"):
        start_time = time.time()
        self.logger = get_logger("grammar_corrector")
        
        self.logger.info("Initializing GrammarCorrector", model_name=model_name)
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)
        self.ollama = OllamaService()
        
        init_time = time.time() - start_time
        self.logger.info("GrammarCorrector initialized successfully",
                   model_name=model_name,
                   device=str(self.device),
                   init_time=round(init_time, 3))

    def infer(self, prompt, max_length=128):
        start_time = time.time()
        
        self.logger.debug("Starting grammar inference",
                    prompt_length=len(prompt),
                    max_length=max_length,
                    device=str(self.device))
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            outputs = self.model.generate(
                **inputs,
                max_length=max_length, 
                num_beams=2, 
                early_stopping=True
            )

            result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            inference_time = time.time() - start_time
            self.logger.info("Grammar inference completed",
                       prompt_length=len(prompt),
                       result_length=len(result),
                       inference_time=round(inference_time, 3))
            
            return result
            
        except Exception as e:
            inference_time = time.time() - start_time
            self.logger.error("Grammar inference failed",
                        error=str(e),
                        inference_time=round(inference_time, 3))
            raise

    def analyse(self, original: str, include_explanations: bool = False):
        """
        Analyse text with grammar correction.

        Args:
            original: Text to analyze (for grammar correction)
            include_explanations: Whether to generate Ollama explanations (default: False for performance)
        """
        start_time = time.time()

        self.logger.info("Starting grammar analysis",
                   original_length=len(original),
                   include_explanations=include_explanations)

        corrected = self.infer(original)
        paragraph_diffs = diff_original_with_corrected(original, corrected)
        grammar_time = time.time() - start_time
        self.logger.info("Grammar analysis completed",
                   grammar_time=round(grammar_time, 3),
                   diff_count=len(paragraph_diffs))

        # Split both paragraphs into sentences
        original_sentences = split_into_sentences(original)
        corrected_sentences = split_into_sentences(corrected)

        self.logger.debug("Sentence analysis",
                    original_sentences=len(original_sentences),
                    corrected_sentences=len(corrected_sentences))

        sentences_analysis = []
        for i, (orig_sent, corr_sent) in enumerate(zip(original_sentences, corrected_sentences)):
            sentence_diffs = diff_original_with_corrected(orig_sent, corr_sent)
            explanation = None
            if include_explanations and sentence_diffs:
                self.logger.debug(f"Generating explanation for sentence {i+1}/{len(original_sentences)}")
                raw_explanation = self.ollama.generate_correction_explanation(orig_sent, corr_sent, sentence_diffs)
                try:
                    explanation_json = json.loads(raw_explanation)
                    explanation = explanation_json.get("message", raw_explanation)
                except Exception:
                    explanation = raw_explanation.strip()
            elif not include_explanations:
                explanation = "Explanations disabled for performance"
            else:
                explanation = "No corrections needed. Your text looks good!"
            sentences_analysis.append({
                "sentenceIndex": i,
                "original": orig_sent,
                "corrected": corr_sent,
                "changes": sentence_diffs,
                "explanation": explanation
            })

        # Handle edge cases for sentence count differences
        if len(corrected_sentences) > len(original_sentences):
            self.logger.warning("Corrected text has more sentences than original",
                          original_count=len(original_sentences),
                          corrected_count=len(corrected_sentences))
            for i in range(len(original_sentences), len(corrected_sentences)):
                sentences_analysis.append({
                    "sentenceIndex": i,
                    "original": "",
                    "corrected": corrected_sentences[i],
                    "changes": [],
                    "explanation": "New sentence added."
                })
        elif len(original_sentences) > len(corrected_sentences):
            self.logger.warning("Original text has more sentences than corrected",
                          original_count=len(original_sentences),
                          corrected_count=len(corrected_sentences))
            for i in range(len(corrected_sentences), len(original_sentences)):
                sentences_analysis.append({
                    "sentenceIndex": i,
                    "original": original_sentences[i],
                    "corrected": "",
                    "changes": [],
                    "explanation": "Sentence removed."
                })

        total_time = time.time() - start_time
        self.logger.info("Grammar analysis completed",
                   total_time=round(total_time, 3),
                   sentence_count=len(sentences_analysis))

        response = {
            "original": original,
            "corrected": corrected,
            "paragraphDiffs": paragraph_diffs,
            "sentences": sentences_analysis
        }
        return response