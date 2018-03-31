"""
ReactionSystem is a Python library for manage for manage Reaction System. 
It depends on boolexpr and pyeda.
"""

try:
    import boolexpr
except ImportError:
    raise ImportError("ReactionSystem depends on boolexpr as an external library. ")
del boolexpr

try:
    import pyeda
except ImportError:
    raise ImportError("ReactionSystem depends on pyeda as an external library. ")
del pyeda

import sys
if sys.version_info[0] < 2:
    raise ImportError("Python version 3 for ReactionSystem.")
del sys

from .var import var
from .reaction_system import *
from .exceptions import *