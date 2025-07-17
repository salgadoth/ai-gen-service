import json
from typing import List, Dict, Any, Optional
from utils.split import split_into_sentences
from utils.logger import get_logger
import ollama
import time
import re

class InsufficientContentError(Exception):
    """Raised when content doesn't meet minimum requirements for insights analysis"""
    def __init__(self, min_sentences: int, min_words: int):
        self.min_sentences = min_sentences
        self.min_words = min_words
        super().__init__(f"Need at least {min_sentences} sentences and {min_words} words for insights analysis")

class OllamaService:
    def __init__(self, model_name: str = "llama3.2:latest", 
                 min_sentences: int = 3, min_words: int = 50):
        self.model_name = model_name
        self.min_sentences = min_sentences
        self.min_words = min_words
        self.logger = get_logger("ollama_service")
        
        self.logger.info("OllamaService initialized", 
                   model_name=model_name,
                   min_sentences=min_sentences,
                   min_words=min_words)
        
    def _meets_threshold(self, text: str) -> bool:
        """Check if text meets minimum requirements for insights analysis"""
        sentences = split_into_sentences(text)
        word_count = len(text.split())
        
        meets_threshold = len(sentences) >= self.min_sentences and word_count >= self.min_words
        
        self.logger.debug("Content threshold check",
                    text_length=len(text),
                    sentence_count=len(sentences),
                    word_count=word_count,
                    meets_threshold=meets_threshold)
        
        return meets_threshold
        
    def generate(self, prompt: str, system: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> dict:
        """Generate text using Ollama Python package (using generate, not chat)"""
        start_time = time.time()
        
        try:
            self.logger.debug("Starting Ollama generation (generate)",
                        model_name=self.model_name,
                        prompt_length=len(prompt),
                        has_system=system is not None,
                        has_options=options is not None)
            
            # Prepare the generate call parameters
            generate_params = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            
            # Add options if provided
            if options:
                generate_params["options"] = options
            
            # Use ollama.generate instead of ollama.chat
            response = ollama.generate(**generate_params)
            
            generation_time = time.time() - start_time
            response_text = response["response"] if "response" in response else ""
            response_length = len(response_text)
            
            self.logger.info("Ollama generation completed",
                       model_name=self.model_name,
                       generation_time=round(generation_time, 3),
                       response_length=response_length)
            
            response_text = response_text.replace("\n", "")
            json_match = re.search(r'(\{.*\}|\[.*\])', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    parsed = json.loads(json_str)
                    return parsed
                except json.JSONDecodeError as e:
                    self.logger.error("Failed to parse Ollama response as JSON", error=str(e), raw_response=json_str)
                    return {"error": "Invalid JSON format", "raw": response_text}
            else:
                self.logger.error("No JSON found in Ollama response", raw_response=response_text)
                return {"error": "No JSON found in response", "raw": response_text}

        except Exception as e:
            generation_time = time.time() - start_time
            self.logger.error("Ollama generation failed",
                        model_name=self.model_name,
                        error=str(e),
                        generation_time=round(generation_time, 3))
            return {"error": "Ollama generation failed", "raw": str(e)}
    
    def generate_batch_explanations(self, corrections_batch: List[str]):
        """Generate explanations for multiple corrections in one call using the provided system prompt."""
        if not corrections_batch:
            return "No corrections to explain."
        
        # Build the user block for all corrections
        user_block = "\n".join(corrections_batch)
        
        prompt = f'''
            <|system|>
            You are a helpful and precise grammar coach.
            Your job is to describe, in a short and objective way, what has changed between the two versions of a sentence.
            Do NOT evaluate the quality of the change. Only describe the difference.

            Apply the following chain of thought:
            1. Compare the original and corrected versions line by line.
            2. For each line, detect the differences.
            3. For each difference, describe exactly what was changed (e.g., a word replacement, verb tense change, punctuation correction).
            4. Do not explain whether the change is good or bad. Do not rewrite the sentence again.
            5. Combine these into a single concise message, written clearly for the end user.

            Do not suggest or apply additional corrections. Only explain what was changed.
            Avoid vague or generalised comments.
            Avoid restating the full sentence. Focus only on the change.

            Output format:
            {{
                "message": "Changed X to Y because Z."
                "delta": Float, from 0 to 1, how confident are you on the analysis.
            }}
            <|end|>

            <|user|>
            {user_block}
            <|end|>

            <|assistant|>
            '''
        
        return self.generate(prompt)

    def generate_correction_explanation(self, original: str, corrected: str, changes: List[dict]):
        """Generate explanation for a single grammar correction using the provided system prompt."""
        if not changes:
            return "No corrections needed. Your text looks good!"
        prompt = f'''
            <|system|>
            You are a helpful and precise grammar coach.
            Your job is to describe, in a short and objective way, what has changed between the two versions of a sentence.
            Do NOT evaluate the quality of the change. Only describe the difference.

            Apply the following chain of thought:
            1. Compare the original and corrected versions line by line.
            2. For each line, detect the differences.
            3. For each difference, describe exactly what was changed (e.g., a word replacement, verb tense change, punctuation correction).
            4. Do not explain whether the change is good or bad. Do not rewrite the sentence again.
            5. Combine these into a single concise message, written clearly for the end user.

            Do not suggest or apply additional corrections. Only explain what was changed.
            Avoid vague or generalised comments.
            Avoid restating the full sentence. Focus only on the change.

            Output format:
            {{
                "message": "Changed X to Y because Z."
                "delta": Float, from 0 to 1, how confident are you on the analysis.
            }}
            <|end|>

            <|user|>
            Original: "{original}"
            Corrected: "{corrected}"
            <|end|>

            <|assistant|>
            '''
        return self.generate(prompt)
    
    def generate_content_insights(self, text: str, full_context: Optional[str] = None):
        """Generate research insights, thought starters, and content references"""
        # Use full context if available, otherwise use the provided text
        context_to_analyze = full_context if full_context else text

        self.logger.info("Generating content insights",
                   text_length=len(text),
                   context_length=len(context_to_analyze),
                   has_full_context=full_context is not None)
        
        # Check if we have enough content for meaningful insights
        if not self._meets_threshold(context_to_analyze):
            self.logger.warning("Insufficient content for insights analysis",
                          text_length=len(context_to_analyze),
                          min_sentences=self.min_sentences,
                          min_words=self.min_words)
            raise InsufficientContentError(self.min_sentences, self.min_words)
            
        prompt = f'''
        <|system|>
        You are a research assistant and content strategist. Analyze the following text and provide valuable insights, thought starters, and references to help expand and enhance the content.

        Your task:
        - Generate 3 distinct, actionable suggestions or insights for the user.
        - Number each suggestion.
        - Be specific and practical.

        Please use the following structure for your suggestions:

        1. **Thought Starters & Ideas**
        - Related topics and angles to explore
        - Questions that could deepen the discussion
        - Alternative perspectives to consider

        2. **Research References & Sources**
        - Suggest relevant articles, papers, or studies
        - Recommend authoritative sources on the topic
        - Point to current trends or developments

        3. **Data & Statistics**
        - Suggest relevant data points or statistics
        - Recommend sources for quantitative insights
        - Highlight key metrics to consider

        4. **Content Expansion Opportunities**
        - Related subtopics to explore
        - Examples or case studies to include
        - Additional context that would strengthen the argument

        5. **Current Events & Trends**
        - Recent developments related to the topic
        - Emerging trends or discussions
        - Timely angles to consider

        Focus on providing actionable, specific suggestions that will help the writer expand their content with credible, relevant information.
        Keep suggestions practical and directly related to the content's themes and goals.

        CRITICAL OUTPUT REQUIREMENTS:
        - You MUST respond with ONLY valid JSON that can be parsed by Python's json.loads()
        - Start with {{ and end with }}
        - Use double quotes for all strings
        - Use proper JSON syntax (commas, brackets, etc.)
        - No trailing commas
        - No comments or explanations outside the JSON
        - No markdown formatting
        - No need to break lines

        Required JSON structure:
        [
            {{
                "id": 1,
                "category": "Thought Starters & Ideas",
                "suggestion": "Your specific suggestion here",
                "description": "Brief explanation of why this is valuable"
                "references": ["link 1 or title 1", "link 2 or title 2", "link 3 or title 3"]
            }},
            {{
                "id": 2,
                "category": "Research References & Sources",
                "suggestion": "Your specific suggestion here",
                "description": "Brief explanation of why this is valuable"
                "references": ["link 1 or title 1", "link 2 or title 2", "link 3 or title 3"]
            }},
            {{
                "id": 3,
                "category": "Data & Statistics",
                "suggestion": "Your specific suggestion here",
                "description": "Brief explanation of why this is valuable"
                "references": ["link 1 or title 1", "link 2 or title 2", "link 3 or title 3"]
            }},
            {{
                "id": 4,
                "category": "Content Expansion Opportunities",
                "suggestion": "Your specific suggestion here",
                "description": "Brief explanation of why this is valuable"
                "references": ["link 1 or title 1", "link 2 or title 2", "link 3 or title 3"]
            }},
        ]

        DO NOT include any text before or after the JSON. Only return the JSON object.
        <|end|>

        <|user|>
        TEXT TO ANALYZE:
        {text}
        <|end|>

        <|assistant|>
        '''
        return self.generate(prompt, options={"temperature": 0.1, "top_p": 0.9})
    
    def generate_combined_analysis(self, text: str, full_context: Optional[str] = None):
        """Generate both grammar explanations and content insights"""
        return {
            "insights": self.generate_content_insights(text, full_context)
        } 