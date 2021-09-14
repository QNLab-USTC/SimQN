import logging
import sys

log = logging.getLogger("qns")
"""
The default ``logger`` used by QuantNetSim
"""

log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stdout))