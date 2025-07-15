#!/usr/bin/env python3
"""
Test script to demonstrate performance improvements
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.grammar_corrector import GrammarCorrector

def test_performance():
    """Test performance with and without explanations"""
    
    # Initialize the model
    print("Initializing GrammarCorrector...")
    model = GrammarCorrector()
    
    # Test text with multiple sentences
    test_text = """
    This sentence has error. Here is another sentence with mistake. 
    The third sentence is also incorrect. This is the fourth sentence with problems.
    Finally, this is the last sentence that needs correction.
    """
    
    print(f"\nTesting with text: {test_text.strip()}")
    
    # Test 1: With explanations (slower but more detailed)
    print("\n=== Test 1: With Explanations ===")
    start_time = time.time()
    time_with_explanations = None
    
    try:
        result_with_explanations = model.analyse(
            original=test_text,
            include_explanations=True
        )
        
        time_with_explanations = time.time() - start_time
        print(f"✅ Completed in {time_with_explanations:.2f} seconds")
        print(f"   Sentences processed: {len(result_with_explanations['sentences'])}")
        print(f"   Explanations generated: {sum(1 for s in result_with_explanations['sentences'] if s['explanation'] and 'Explanations disabled' not in s['explanation'])}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 2: Without explanations (faster)
    print("\n=== Test 2: Without Explanations ===")
    start_time = time.time()
    time_without_explanations = None
    
    try:
        result_without_explanations = model.analyse(
            original=test_text,
            include_explanations=False
        )
        
        time_without_explanations = time.time() - start_time
        print(f"✅ Completed in {time_without_explanations:.2f} seconds")
        print(f"   Sentences processed: {len(result_without_explanations['sentences'])}")
        print(f"   Explanations generated: {sum(1 for s in result_without_explanations['sentences'] if s['explanation'] and 'Explanations disabled' not in s['explanation'])}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Performance comparison
    if (
        time_with_explanations is not None and time_without_explanations is not None and
        time_without_explanations > 0
    ):
        speedup = time_with_explanations / time_without_explanations
        print(f"\n=== Performance Summary ===")
        print(f"With explanations: {time_with_explanations:.2f}s")
        print(f"Without explanations: {time_without_explanations:.2f}s")
        print(f"Speedup: {speedup:.1f}x faster without explanations")

if __name__ == "__main__":
    test_performance() 