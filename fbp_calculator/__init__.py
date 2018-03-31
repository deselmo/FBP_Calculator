"""
FBP Calculator is a Python tool to calculate predicor for Reaction System.
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

try:
    import PyQt5
except ImportError:
    raise ImportError("ReactionSystem depends on PyQt5 as an external library. ")
del PyQt5

try:
    import xlsxwriter
except ImportError:
    raise ImportError("ReactionSystem depends on xlsxwriter as an external library. ")
del xlsxwriter

import sys
if sys.version_info[0] < 2:
    raise ImportError("Python version 3 for ReactionSystem.")
del sys

from fbp_calculator.__main__ import main