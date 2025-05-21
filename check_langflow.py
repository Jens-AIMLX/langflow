import sys
import os
import importlib.util

# Activate the virtual environment
venv_path = os.path.join(os.getcwd(), "langflow_venv")
site_packages = os.path.join(venv_path, "Lib", "site-packages")

print(f"Checking if virtual environment exists at: {venv_path}")
if not os.path.exists(venv_path):
    print("Virtual environment not found!")
    sys.exit(1)

print(f"Checking site-packages at: {site_packages}")
if not os.path.exists(site_packages):
    print("Site-packages directory not found!")
    sys.exit(1)

# Add site-packages to Python path
sys.path.insert(0, site_packages)

# Check if typer is installed
print("Checking if typer is installed...")
typer_spec = importlib.util.find_spec("typer")
if typer_spec is None:
    print("typer is not installed!")
else:
    print(f"typer is installed at: {typer_spec.origin}")

# Check if langflow is installed
print("Checking if langflow is installed...")
langflow_spec = importlib.util.find_spec("langflow")
if langflow_spec is None:
    print("langflow is not installed!")
else:
    print(f"langflow is installed at: {langflow_spec.origin}")

# Try to import langflow
try:
    import langflow
    print(f"Successfully imported langflow version: {langflow.__version__}")
except ImportError as e:
    print(f"Failed to import langflow: {e}")

# Try to import langflow.__main__
try:
    from langflow import __main__
    print("Successfully imported langflow.__main__")
except ImportError as e:
    print(f"Failed to import langflow.__main__: {e}")

# Print Python path
print("\nPython path:")
for path in sys.path:
    print(f"  - {path}")
