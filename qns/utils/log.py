import logging
import sys

log = logging.getLogger("qns")
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stdout))