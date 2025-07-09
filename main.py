import os
from PIL import Image
import logging
from logging.handlers import QueueHandler, QueueListener
import queue
import threading

# Set up logging
log_queue = queue.Queue()
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('logs/main.log'), logging.StreamHandler()]
)
queue_listener = QueueListener(log_queue, logging.StreamHandler())
queue_listener.start()

def log(message, level=logging.INFO):
    """
    Logs a message to the log file and console.
    """
    logger = logging.getLogger(__name__)
    logger.addHandler(QueueHandler(log_queue))  # Thread-safe logging
    logger.setLevel(logging.INFO)
    logger.log(level, message)

def convertImage(input_path, output_path):
    """
    Converts a .tiff image to .jpeg format.
    """
    try:
        with Image.open(input_path) as img:
            img.convert("RGB").save(output_path, "JPEG")
        log(f"Converted {input_path} to {output_path} successfully.")
    except Exception as e:
        log(f"Failed to convert {input_path} to {output_path}: {e}", level=logging.ERROR)
