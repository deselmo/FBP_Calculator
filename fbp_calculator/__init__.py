# -*- coding: utf-8 -*-

"""
FBP Calculator is a Python tool to calculate predicor for Reaction System.
"""

from fbp_calculator.release import __version__

import sys
if not (sys.version_info[0] == 3 and sys.version_info[1] >= 3):
    raise ImportError("Python version 3.3 or above is required.")
del sys

try:
    import PyQt5
except ImportError:
    raise ImportError("fbp_calculator depends on PyQt5 as an external library. ")
del PyQt5

try:
    import xlsxwriter
except ImportError:
    raise ImportError("fbp_calculator depends on xlsxwriter as an external library. ")
del xlsxwriter

import sys
if sys.version_info[0] < 2:
    raise ImportError("Python version 3 for ReactionSystem.")
del sys

from fbp_calculator.main import main
