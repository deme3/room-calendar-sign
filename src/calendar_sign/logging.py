import logging
from rich.logging import RichHandler
from pathlib import Path

THIS_SCRIPT = Path(__file__).resolve()
THIS_SCRIPT_DIR = THIS_SCRIPT.parent
SRC_DIR = THIS_SCRIPT_DIR.parent
ROOT_DIR = SRC_DIR.parent
LOGS_DIR = ROOT_DIR / 'logs'

if not LOGS_DIR.exists():
  LOGS_DIR.mkdir()

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler with RichHandler
console_handler = RichHandler(show_time=True)
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

# Create file handler
file_handler = logging.FileHandler(LOGS_DIR / 'calendar.log')
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# Create formatter
console_formatter = logging.Formatter('%(message)s')
file_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] - %(message)s')

# Set formatter for handlers
console_handler.setFormatter(console_formatter)
file_handler.setFormatter(file_formatter)
