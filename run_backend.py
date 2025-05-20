import sys 
import os 
sys.path.extend([r'C:\Users\jenss\OneDrive - Singularyt UG\Code\source\Dev\Langflow\langflow', r'C:\Users\jenss\OneDrive - Singularyt UG\Code\source\Dev\Langflow\langflow\src', r'C:\Users\jenss\OneDrive - Singularyt UG\Code\source\Dev\Langflow\langflow\src\backend', r'C:\Users\jenss\OneDrive - Singularyt UG\Code\source\Dev\Langflow\langflow\src\backend\base']) 
from src.backend.base.langflow.__main__ import run_langflow 
print('Starting LangFlow backend on port 7860...') 
run_langflow('0.0.0.0', 7860, 'debug', {}, None) 
