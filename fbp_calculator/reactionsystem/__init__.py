"""
ReactionSystem is a Python library for manage for manage Reaction System. 
It depends on boolexpr and pyeda.
"""

import sys
if not (sys.version_info[0] == 3 and sys.version_info[1] >= 3):
    raise ImportError("Python version 3.3 or above is required.")
del sys

try:
    import pyeda
except ImportError:
    raise ImportError("ReactionSystem depends on pyeda as an external library. ")
del pyeda

import sys
if sys.version_info[0] < 2:
    raise ImportError("Python version 3 for ReactionSystem.")
del sys

from .reaction_system import *
from .exceptions import *
