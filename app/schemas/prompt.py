from pydantic import BaseModel
from typing import List, Optional, Union

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

class Insight(BaseModel):
    id: int # The id of the insight
    category: str # The category of the insight
    suggestion: str # The suggestion of the insight
    description: str # The description of the insight
    references: Optional[List[str]] = None # The references of the insight

class InsightsResponse(BaseModel):
    insights: List[Insight] # The generated insights

class ErrorResponse(BaseModel):
    error: str # The error message
    raw: Optional[str] = None # The raw response from the model

OllamaGeneralResult = Union[InsightsResponse, ErrorResponse]