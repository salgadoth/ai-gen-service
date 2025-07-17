import logging
import structlog
from pathlib import Path
from datetime import datetime
from typing import Optional

def setup_structlog(log_level: str = "DEBUG", log_file: Optional[str] = None):
    # Create a custom formatter for JSON file output
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            # Extract structured data from the record
            message = record.getMessage()
            
            # Parse the structured log message to extract fields
            import re
            
            # Extract timestamp, level, logger, and event
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)', message)
            level_match = re.search(r'\[(\w+)\s+\]', message)
            logger_match = re.search(r'\[([^\]]+)\]', message)
            
            # Extract key-value pairs
            kv_pairs = re.findall(r'(\w+)=([^\s]+)', message)
            
            # Build JSON structure
            log_entry = {
                "timestamp": timestamp_match.group(1) if timestamp_match else datetime.now().isoformat(),
                "level": level_match.group(1) if level_match else record.levelname.lower(),
                "logger": logger_match.group(1).strip() if logger_match else record.name.strip(),
                "event": message.split('[')[0].strip() if '[' in message else message,
            }
            
            # Add key-value pairs
            for key, value in kv_pairs:
                # Clean up the value (quotes)
                clean_value = value.strip('"\'')  # Remove quotes
                log_entry[key] = clean_value
            
            import json
            return json.dumps(log_entry)

    # Console handler (human-readable)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter("%(message)s"))

    # File handler (JSON)
    file_handler = None
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(JSONFormatter())

    # Remove all handlers before adding new ones (avoid duplicates)
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    if file_handler:
        root_logger.addHandler(file_handler)

    # Configure structlog for console (default logger)
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer(colors=False)  # Console only
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

# Initialize logging on module import
def init_logging():
    logs_dir = Path(".logs")
    logs_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = logs_dir / f"app_{timestamp}.log"
    setup_structlog(log_level="DEBUG", log_file=str(log_file))

init_logging()

def get_logger(name: str):
    return structlog.get_logger(name) 