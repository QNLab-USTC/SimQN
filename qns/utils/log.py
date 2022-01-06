import logging
import sys

logger = logging.getLogger("qns")
"""
The default ``logger`` used by SimQN
"""

logger.setLevel(logging.INFO)
handle = logging.StreamHandler(sys.stdout)
logger.addHandler(handle)


def install(s):
    """
    Install the logger to the simulator

    Args:
        s (Simulator): the simulator
    """
    logger._simulator = s


def debug(msg, *args):
    if hasattr(logger, "_simulator"):
        logger.debug(f"[{logger._simulator.tc}] " + msg, *args)
    else:
        logger.debug(msg, *args)


def info(msg, *args):
    if hasattr(logger, "_simulator"):
        logger.info(f"[{logger._simulator.tc}] " + msg, *args)
    else:
        logger.info(msg, *args)


def error(msg, *args):
    if hasattr(logger, "_simulator"):
        logger.error(f"[{logger._simulator.tc}] " + msg, *args)
    else:
        logger.error(msg, *args)


def warn(msg, *args):
    if hasattr(logger, "_simulator"):
        logger.warn(f"[{logger._simulator.tc}] " + msg, *args)
    else:
        logger.warn(msg, *args)


def critical(msg, *args):
    if hasattr(logger, "_simulator"):
        logger.critical(f"[{logger._simulator.tc}] " + msg, *args)
    else:
        logger.critical(msg, *args)


def monitor(*args, sep: str = ",", with_time: bool = False):
    attrs = list(args)
    if with_time:
        attrs.insert(0, logger._simulator.tc)
    attrs_s = [str(a) for a in attrs]
    msg = sep.join(attrs_s)
    logger.info(msg)
