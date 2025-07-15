#!/usr/bin/env python3
"""
Test script to demonstrate structured logging
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.logger import get_logger

def test_structured_logging():
    """Test the structured logging functionality"""
    
    # Get logger
    logger = get_logger("test")
    
    print("=== Testing Structured Logging ===\n")
    
    # Test different log levels
    logger.debug("This is a debug message", user_id=123, action="test")
    logger.info("This is an info message", service="test-service", version="1.0")
    logger.warning("This is a warning message", error_code=404, path="/test")
    logger.error("This is an error message", exception="TestException", stack_trace="...")
    
    # Test with structured data
    logger.info("User action completed",
               user_id=456,
               action="grammar_check",
               text_length=150,
               processing_time=0.234,
               status="success")
    
    # Test error with context
    try:
        raise ValueError("Test error for logging")
    except Exception as e:
        logger.error("An error occurred during processing",
                    error_type=type(e).__name__,
                    error_message=str(e),
                    context="test_function")
    
    print("\n=== Check the logs/app_YYYYMMDD.log file for JSON formatted logs ===")

if __name__ == "__main__":
    test_structured_logging() 