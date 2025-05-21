import sys
import os

# Set up paths
base_dir = os.getcwd()
# Add site-packages directory to the Python path
site_packages = os.path.join(base_dir, 'langflow_venv', 'Lib', 'site-packages')
if os.path.exists(site_packages):
    sys.path.insert(0, site_packages)

sys.path.extend([base_dir,
                 os.path.join(base_dir, 'src'),
                 os.path.join(base_dir, 'src', 'backend'),
                 os.path.join(base_dir, 'src', 'backend', 'base')])

# Print Python path for debugging
print("Python path:", sys.path)

# Import the run_langflow function
from src.backend.base.langflow.__main__ import run_langflow

print('Starting LangFlow backend on port 7860...')
run_langflow('0.0.0.0', 7860, 'debug', {}, None)
