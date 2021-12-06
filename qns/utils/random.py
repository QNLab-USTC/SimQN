import random
from typing import Optional
import numpy as np


def set_seed(seed: Optional[int] = None):
    """
    Set a seed for random generator

    Args:
        seed (int): the seed
    """
    if seed is None:
        return
    random.seed(seed)
    np.random.seed(seed)
