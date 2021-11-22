import logging
import sys

logger = logging.getLogger("qns")
"""
The default ``logger`` used by QuantNetSim
"""

logger.setLevel(logging.INFO)
handle = logging.StreamHandler(sys.stdout)
logger.addHandler(handle)

def install(s: "Simulator"):
    logger._simulator = s

def debug(msg, *args):
    if hasattr(logger, "_simulator"):
        logger.debug(f"[{logger._simulator.tc}] "+msg, *args)
    else:
        logger.debug(msg, *args)

def info(msg, *args):
    if hasattr(logger, "_simulator"):
        logger.info(f"[{logger._simulator.tc}] "+msg, *args)
    else:
        logger.info(msg, *args)

def error(msg, *args):
    if hasattr(logger, "_simulator"):
        logger.error(f"[{logger._simulator.tc}] "+msg, *args)
    else:
        logger.error(msg, *args)

def warn(msg, *args):
    if hasattr(logger, "_simulator"):
        logger.warn(f"[{logger._simulator.tc}] "+msg, *args)
    else:
        logger.warn(msg, *args)

def critical(msg, *args):
    if hasattr(logger, "_simulator"):
        logger.critical(f"[{logger._simulator.tc}] "+msg, *args)
    else:
        logger.critical(msg, *args)

def monitor(attrs, sep: str = ",", with_time: bool = False):
    if isinstance(attrs, list):
        if with_time and hasattr(logger, "_simulator"):
            attrs.append(logger._simulator.tc)
        logger.info(sep.join(attrs))
        return
    if with_time and hasattr(logger, "_simulator"):
        attrs = [attrs, logger._simulator.tc]
    logger.info(attrs)