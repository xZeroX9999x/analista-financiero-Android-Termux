
# config.py
import logging
import os
from pathlib import Path

# Constantes del sistema
VERSION = "2.1.0-Termux-Modular"
CACHE_DIR = Path.home() / ".analista_financiero_cache"
OUTPUT_DIR = Path.cwd() / "output"
CACHE_TTL_HOURS = 24
MAX_RETRIES = 3
BACKOFF_FACTOR = 2
TIMEOUT_SECONDS = 30

# Configuración de API Key
GROK_API_KEY = os.getenv("TUAPIDEGROKAQUI")

# Configuración de logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("AnalistaFinanciero")
