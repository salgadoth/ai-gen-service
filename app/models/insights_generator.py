from typing import Optional, List, Any
from models.ollama_service import OllamaService
from utils.logger import get_logger
import json

class InsightsGenerator:
    def __init__(self):
        self.ollama = OllamaService()
        self.logger = get_logger("insights_generator")

    def generate(self, text: str, full_context: Optional[str] = None):
        """
        Generate insights using OllamaService and parse the response as JSON.
        Args:
            text: The main text to analyze.
            full_context: Optional broader context for insights analysis.
        Returns:
            List of insights (as required by the endpoint).
        Raises:
            Exception if insights cannot be generated or parsed.
        """
        try:
            return self.ollama.generate_content_insights(text, full_context)        
        except Exception as e:
            self.logger.error("Failed to generate insights", error=str(e))
            raise