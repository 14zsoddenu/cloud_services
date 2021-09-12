from threading import current_thread

from django.utils import timezone
from loguru import logger

from config import CRAZY_PRINTER_MODE
from constants import PRECISE_DATETIME_STRING_TEMPLATE


def time_aware_print(s: str, *args, **kwargs):
    name = current_thread().name
    print(f"[{timezone.now().strftime(PRECISE_DATETIME_STRING_TEMPLATE)}] [{name}] {s}")


if CRAZY_PRINTER_MODE:
    logger.debug = time_aware_print
    logger.info = time_aware_print
    logger.warning = time_aware_print
    logger.error = time_aware_print
    logger.critical = time_aware_print
