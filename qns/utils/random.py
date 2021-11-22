import random
from typing import Optional
import numpy as np

def set_seed(seed: Optional[int] = None):
    """
    Set a seed for random generator
    """
    if seed is None:
        return
    random.seed(seed)
    np.random.seed(seed)