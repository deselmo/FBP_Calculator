"""
ReactionSystem is a Python library for manage for manage Reaction System. 
It depends on boolexpr.
"""

try:
    import boolexpr
except ImportError:
    raise ImportError("ReactionSystem depends on boolexpr as an external library. ")
del boolexpr

from reactionsystem.release import __version__

import sys
if sys.version_info[0] < 2:
    raise ImportError("Python version 3 for ReactionSystem.")
del sys


from .var import var
from .reaction_system import *
from .exceptions import *