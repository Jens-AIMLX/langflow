# Langflow package wrapper 
"""Wrapper for langflow-base""" 
import sys 
import os 
 
# Add base to path for proper imports 
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../base")) 
if base_path not in sys.path: 
    sys.path.insert(0, base_path) 
 
# Import all from the actual implementation 
from src.backend.base.langflow import * 
 
# Make __main__ accessible 
from src.backend.base.langflow.__main__ import run_langflow 
