#!/usr/bin/env python3
"""
Test script to demonstrate base rate responses
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.ollama_service import OllamaService

def test_base_rate_responses():
    # Initialize Ollama service with default thresholds
    ollama = OllamaService(min_sentences=3, min_words=50)
    
    # Test 1: Short text (doesn't meet base rate)
    short_text = "This is a short sentence."
    
    print("=== TEST 1: Short Text (Base Rate NOT Met) ===")
    print(f"Text: '{short_text}'")
    print(f"Meets base rate: {ollama._meets_threshold(short_text)}")
    
    # Test insights generation
    insights_response = ollama.generate_content_insights(short_text)
    print(f"\nInsights Response:")
    print(f"'{insights_response}'")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Longer text (meets base rate)
    long_text = "Climate change is a pressing global issue. Scientists have observed significant temperature increases over the past century. These changes are primarily driven by human activities such as burning fossil fuels. The consequences include rising sea levels, extreme weather events, and ecosystem disruptions."
    
    print("=== TEST 2: Longer Text (Base Rate Met) ===")
    print(f"Text: '{long_text}'")
    print(f"Meets base rate: {ollama._meets_threshold(long_text)}")
    
    # Test insights generation (this would call Ollama API)
    print(f"\nInsights Response: (Would call Ollama API)")
    print("Would return research insights, thought starters, etc.")

if __name__ == "__main__":
    test_base_rate_responses() 