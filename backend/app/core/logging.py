import logging
import sys
import os

def setup_logging(name: str = "app"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if setup is called multiple times
    if logger.handlers:
        return logger

    # Ensure log directory exists
    os.makedirs("/app/data/logs", exist_ok=True)

    # File handler for common logs
    file_handler = logging.FileHandler("/app/data/logs/app.log")
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Standard out handler (optional, but good for docker logs)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
        
    return logger
