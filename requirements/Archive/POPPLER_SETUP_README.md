# PDF to Images Component - Poppler Integration

## About the Component

The PDF to Images component in Langflow requires the Poppler library to convert PDF files to images. We've now integrated Poppler as a seamless dependency of Langflow - no configuration needed.

## Automatic Installation and Detection

Poppler is now automatically installed and detected:

1. **Invisible Dependency**: Poppler is installed as part of the Langflow environment without requiring any user configuration.

2. **Auto-Detection**: The component automatically finds the Poppler installation - no need to specify any paths.

3. **Self-Healing System**: The `run_langflow.bat` script ensures Poppler is installed before launching Langflow.

## How to Use

Simply follow these steps:

1. **New Installation**: Run `install_langflow_uv.bat` to set up Langflow with Poppler included.

2. **Existing Installation**: Run `run_langflow.bat` to start Langflow - it will automatically install Poppler if needed.

3. **Using the Component**: The PDF to Images component works without any configuration - just connect it to your PDF file input.

## Troubleshooting

If you encounter issues:

1. **Check the Logs**: Look for messages about Poppler path detection in the Langflow logs.

2. **Reinstall**: Run `install_poppler.bat` to reinstall Poppler separately.

3. **Path Issues**: Ensure the Langflow virtual environment can find the Poppler binaries.

## For Developers

The integration works through these mechanisms:

1. Poppler is installed to `langflow_venv/poppler/`
2. The PATH environment variable is updated in the virtual environment's activation script
3. The component uses automatic path detection to find Poppler in common locations

## Additional Resources

- [pdf2image Documentation](https://pypi.org/project/pdf2image/)
- [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases) 