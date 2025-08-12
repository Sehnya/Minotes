# Ensure project root is on sys.path so that 'app' package can be imported
import os
import sys
ROOT = os.path.dirname(__file__)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
