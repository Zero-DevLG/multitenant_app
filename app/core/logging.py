import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

class FlushingRotatingFileHandler(RotatingFileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

def get_logger(channel: str) -> logging.Logger:
    logger = logging.getLogger(channel)
    logger.setLevel(logging.INFO)
    logger.disabled = False
    
    # Revisa si no tiene handlers agregados para evitar duplicación
    if not logger.handlers:
        # Handler para Archivo
        file_handler = FlushingRotatingFileHandler(
            LOG_DIR / f"{channel}.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        
        # Handler para Consola (para verificar en la terminal de FastAPI)
        stream_handler = logging.StreamHandler()
        
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        logger.propagate = False
        
    return logger