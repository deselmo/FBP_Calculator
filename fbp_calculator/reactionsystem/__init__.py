"""
ReactionSystem is a Python library for manage for manage Reaction System. 
It depends on Sympy.
"""

try:
    import sympy
except ImportError:
    raise ImportError("ReactionSystem depends on sympy as an external library. ")
del sympy

from reactionsystem.release import __version__

import sys
if sys.version_info[0] < 2:
    raise ImportError("Python version 3 for ReactionSystem.")
del sys


from .reaction_system import *
from .exceptions import *