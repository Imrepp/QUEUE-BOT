"""
logger.py — Handles all logging to both console and a log file.
Works both as .py script and PyInstaller .exe
"""

import logging
import os
import sys
import pathlib
from datetime import datetime

def _get_base_dir():
    if getattr(sys, "frozen", False):
        return pathlib.Path(sys.executable).parent.resolve()
    return pathlib.Path(__file__).parent.resolve()

def setup_logger():
    log_dir = str(_get_base_dir() / "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(log_dir, f"queue_{datetime.now().strftime('%Y-%m-%d')}.log")

    logger = logging.getLogger("MCTiersBot")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(log_filename, encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger


def log_queue_event(logger, server_name: str, event: str, details: str = ""):
    msg = f"[{server_name}] {event}"
    if details:
        msg += f" | {details}"
    logger.info(msg)
