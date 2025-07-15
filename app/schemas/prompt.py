from pydantic import BaseModel
from typing import List, Optional

class Prompt(BaseModel):
    text: str
    full_context: Optional[str] = None  # For insights analysis - broader context
    analysis_type: Optional[str] = "grammar"  # "grammar", "insights", or "both"
    include_explanations: Optional[bool] = False  # Whether to generate Ollama explanations (default: False for performance)

class Change(BaseModel):
    startIndex: int  # Start position of the change
    endIndex: int # End position of the change
    resolution: str # The resolution of the change (empty if deletion / no change)

class SentenceAnalysis(BaseModel):
    sentenceIndex: int # Position of the sentence in paragraph
    original: str # Original sentence
    corrected: str # Corrected sentence
    changes: List[Change] # List of changes in the sentence
    explanation: Optional[str] = None # Ollama-generated explanation of corrections

class GrammarAnalysisResponse(BaseModel):
    original: str # Full original paragraph
    corrected: str # Full corrected paragraph
    paragraphDiffs: List[Change] # List of changes in the paragraph
    sentences: List[SentenceAnalysis] # Detailed sentence by sentence analysis

class InsightsResponse(BaseModel):
    original: str # The original text for which insights were generated
    insights: str # The generated insights string