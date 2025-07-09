import os
from PIL import Image
import logging
from logging.handlers import QueueHandler, QueueListener
import queue
import multiprocessing
import sys

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

def convertFolder(folder):
    """
    Recursively converts all .tiff images in the given folder to .jpeg format.
    """
    results = []
    log(f"Starting conversion in folder: {folder}")
    with multiprocessing.Pool() as pool:
        for root, _, files in os.walk(folder):
            for file in files:
                if file.lower().endswith('.tiff') or file.lower().endswith('.tif'):
                    input_path = os.path.join(root, file)
                    output_path = os.path.join(root, f"{os.path.splitext(file)[0]}-converted.jpeg")
                    results.append(pool.apply_async(convertImage, (input_path, output_path)))
        log(f"Conversion tasks submitted for folder: {folder} with {len(results)} tasks.")
        for result in results:
            result.get()

if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else '.'
    convertFolder(folder)