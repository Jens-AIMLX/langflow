"""Backend package for Langflow"""

import os
import sys

# Ensure base directory is in path
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "base"))
if base_path not in sys.path:
    sys.path.insert(0, base_path) 
