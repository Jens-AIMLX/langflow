import sys 
import os 
 
# Set up paths 
base_dir = os.getcwd() 
sys.path.extend([base_dir, 
                 os.path.join(base_dir, 'src'), 
                 os.path.join(base_dir, 'src', 'backend'), 
                 os.path.join(base_dir, 'src', 'backend', 'base')]) 
 
# Import the run_langflow function 
from src.backend.base.langflow.__main__ import run_langflow 
 
print('Starting LangFlow backend on port 7860...') 
run_langflow('0.0.0.0', 7860, 'debug', {}, None) 
