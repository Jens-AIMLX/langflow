import re 
with open('pyproject.toml', 'r') as f: 
    content = f.read() 
# Update chromadb version to be compatible with crewai 
content = re.sub(r'"chromadb==0.5.23",', '"chromadb>=0.5.23",', content) 
# Remove crewai that conflicts with chromadb 
content = re.sub(r'"crewai==0.102.0",', '"# crewai==0.102.0 # Temporarily disabled due to chromadb conflict",', content) 
# Update Python version constraint to be more permissive 
content = re.sub(r'requires-python = ">=3.10,<3.13"', 'requires-python = ">=3.10,<3.13"', content) 
with open('pyproject.toml', 'w') as f: 
    f.write(content) 
print("Pyproject.toml updated successfully") 
