import sys 
import os 
sys.path.extend([r'D:\dev\Langflow\langflow', r'D:\dev\Langflow\langflow\src', r'D:\dev\Langflow\langflow\src\backend', r'D:\dev\Langflow\langflow\src\backend\base']) 
from src.backend.base.langflow.__main__ import run_langflow 
print('Starting LangFlow backend on port 7860...') 
run_langflow('0.0.0.0', 7860, 'debug', {}, None) 
