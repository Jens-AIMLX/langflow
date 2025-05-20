# Import main module
"""Import the main module from langflow-base"""

import sys
import os

# Add base to path for proper imports
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../base"))
if base_path not in sys.path:
    sys.path.insert(0, base_path)

# Direct import from the base package
from src.backend.base.langflow.main import create_app
