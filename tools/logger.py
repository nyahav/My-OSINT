import logging
import sys

from app.config import app_name, settings

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO, 
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",  
    datefmt="%d/%b/%Y %H:%M:%S",
)
logger = logging.getLogger(app_name)
