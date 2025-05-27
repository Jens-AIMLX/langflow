from typing import List, Optional, Any
from langflow.custom import Component
from langflow.io import StrInput, DataInput, Output
from langflow.schema import Data
from pdf2image import convert_from_path, convert_from_bytes
import os
import sys
import logging

class PdfToImagesComponent(Component):
    """
    Convert each page of a PDF file into separate PNG image files.
    Accepts either:
      • the Data object(s) from a File node (preferred), or
      • a raw path string in pdf_path.
    """
    display_name = "PDF to Images"
    name = "PdfToImagesComponent"
    description = "Wandelt jede Seite eines PDFs in ein PNG-Bild um."
    icon = "file-image"
    
    def __init__(self, **data):
        super().__init__(**data)
        # Initialize logger - fallback to standard logging if component logger isn't available
        self._logger = None
    
    @property
    def logger(self):
        if self._logger is None:
            # Try to get component's logger if available
            component_logger = getattr(super(), "logger", None)
            if component_logger is not None:
                self._logger = component_logger
            else:
                # Fallback to a standard logger
                self._logger = logging.getLogger(self.__class__.__name__)
                if not self._logger.handlers:
                    handler = logging.StreamHandler()
                    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
                    handler.setFormatter(formatter)
                    self._logger.addHandler(handler)
                    self._logger.setLevel(logging.INFO)
        return self._logger
    
    def log_info(self, message):
        """Safely log an info message, handling cases where logger might not be available"""
        try:
            self.logger.info(message)
        except (AttributeError, Exception) as e:
            print(f"PDF to Images - INFO: {message}")
    
    def log_warning(self, message):
        """Safely log a warning message, handling cases where logger might not be available"""
        try:
            self.logger.warning(message)
        except (AttributeError, Exception) as e:
            print(f"PDF to Images - WARNING: {message}")
    
    def log_error(self, message):
        """Safely log an error message, handling cases where logger might not be available"""
        try:
            self.logger.error(message)
        except (AttributeError, Exception) as e:
            print(f"PDF to Images - ERROR: {message}")

    # Auto-detect poppler path from environment
    @staticmethod
    def get_poppler_path():
        # First check if we're in a virtual environment
        venv_path = os.environ.get("VIRTUAL_ENV", "")
        
        # List of potential poppler paths to check
        potential_paths = []
        
        # Check for different directory structures
        if venv_path:
            potential_paths.extend([
                os.path.join(venv_path, "poppler", "Library", "bin"),
                os.path.join(venv_path, "poppler", "poppler-24.02.0", "bin"),
                os.path.join(venv_path, "poppler", "bin")
            ])
        
        # Get the path of the current script/module
        module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Add more potential paths based on known directory structures
        potential_paths.extend([
            os.path.join(module_dir, "langflow_venv", "poppler", "Library", "bin"),
            os.path.join(module_dir, "langflow_venv", "poppler", "poppler-24.02.0", "bin"),
            os.path.join(module_dir, "Release-24.08.0-0", "poppler-24.08.0", "Library", "bin"),
            os.path.join(module_dir, "Release-24.08.0-0", "poppler-24.08.0", "bin"),
            "D:\\dev\\Langflow\\langflow\\Release-24.08.0-0\\poppler-24.08.0\\Library\\bin",
            "D:\\dev\\Langflow\\langflow\\langflow_venv\\poppler\\poppler-24.02.0\\bin",
            "D:\\dev\\Langflow\\langflow\\langflow_venv\\poppler\\Library\\bin",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "poppler", "Library", "bin"),
            "C:\\Program Files\\poppler\\bin",
            "C:\\Program Files (x86)\\poppler\\bin",
        ])
        
        # Try to find pdftoppm.exe in system PATH
        if sys.platform == 'win32':
            exe_name = 'pdftoppm.exe'
        else:
            exe_name = 'pdftoppm'
            
        for path_dir in os.environ.get('PATH', '').split(os.pathsep):
            exe_path = os.path.join(path_dir, exe_name)
            if os.path.isfile(exe_path):
                return path_dir
        
        # Check if any of our potential paths exist
        for path in potential_paths:
            if path and os.path.exists(path):
                # Verify it contains the necessary executables
                if os.path.exists(os.path.join(path, exe_name)):
                    return path
        
        return ""  # Empty string if not found

    inputs = [
        DataInput(
            name="data",
            display_name="File Data",
            info="Data object(s) from a File node (contains file_path or raw bytes).",
            dynamic=True,
            show=True,
        ),
        StrInput(
            name="pdf_path",
            display_name="PDF Path",
            info="Optionaler Dateipfad (z. B. vom File node → Path).",
        ),
    ]

    outputs = [
        Output(
            name="image_paths",
            display_name="Image Paths",
            method="convert_pdf_to_images",
            info="Liste der generierten PNG-Pfade.",
        ),
    ]

    def convert_pdf_to_images(self) -> Data:
        images = None  # will hold our list of PIL images
        
        # Get poppler path automatically
        poppler_path = PdfToImagesComponent.get_poppler_path()
        if poppler_path:
            self.log_info(f"Using Poppler from: {poppler_path}")
        else:
            self.log_warning("No Poppler installation found. PDF conversion may fail.")

        # Log poppler directory contents for debugging
        if poppler_path and os.path.exists(poppler_path):
            try:
                self.log_info(f"Poppler directory contents: {os.listdir(poppler_path)}")
            except Exception as e:
                self.log_error(f"Could not list Poppler directory: {e}")

        # ─── 1) Normalize self.data to a single Data object ───
        data_obj: Optional[Data] = None
        if self.data is not None:
            if isinstance(self.data, list) and len(self.data) > 0:
                data_obj = self.data[0]
            elif not isinstance(self.data, list):
                data_obj = self.data

        # ─── 2) Try extracting file_path from that Data object ───
        if data_obj:
            file_path = getattr(data_obj, "file_path", None)
            if not file_path and isinstance(data_obj.data, dict):
                file_path = data_obj.data.get("file_path")
            if file_path:
                # we have a real filesystem path
                try:
                    self.log_info(f"Converting from file path: {file_path}")
                    images = convert_from_path(file_path, dpi=600, poppler_path=poppler_path)
                    self.log_info(f"Successfully converted PDF from path with poppler at {poppler_path}")
                except Exception as e:
                    self.log_error(f"Error converting from path: {e}")
                    # Try without poppler_path as fallback
                    try:
                        self.log_info("Trying conversion without explicit poppler path")
                        images = convert_from_path(file_path, dpi=600)
                        self.log_info("Conversion successful without explicit poppler path")
                    except Exception as e2:
                        self.log_error(f"Second attempt failed: {e2}")

            # ─── 3) Fallback: try raw bytes in the same Data object ───
            if images is None and isinstance(data_obj.data, dict):
                raw = data_obj.data.get("data") or data_obj.data.get("bytes")
                if isinstance(raw, (bytes, bytearray)):
                    try:
                        self.log_info("Converting from raw bytes")
                        images = convert_from_bytes(raw, dpi=600, poppler_path=poppler_path)
                        self.log_info(f"Successfully converted PDF from bytes with poppler at {poppler_path}")
                    except Exception as e:
                        self.log_error(f"Error converting from bytes: {e}")
                        # Try without poppler_path as fallback
                        try:
                            self.log_info("Trying conversion from bytes without explicit poppler path")
                            images = convert_from_bytes(raw, dpi=600)
                            self.log_info("Conversion from bytes successful without explicit poppler path")
                        except Exception as e2:
                            self.log_error(f"Second bytes attempt failed: {e2}")

        # ─── 4) Final fallback: pdf_path string if nothing above worked ───
        if images is None and self.pdf_path:
            try:
                self.log_info(f"Converting from pdf_path: {self.pdf_path}")
                images = convert_from_path(self.pdf_path, dpi=600, poppler_path=poppler_path)
                self.log_info(f"Successfully converted PDF from pdf_path with poppler at {poppler_path}")
            except Exception as e:
                self.log_error(f"Error with pdf_path: {e}")
                try:
                    self.log_info("Trying final conversion without explicit poppler path")
                    images = convert_from_path(self.pdf_path, dpi=600)
                    self.log_info("Final conversion successful without explicit poppler path")
                except Exception as e2:
                    raise ValueError(f"Konnte PDF nicht per pdf_path laden: {e2}")

        # ─── If still no images, abort ───
        if images is None:
            raise ValueError("Keine gültigen PDF-Daten gefunden (weder data noch pdf_path).")

        # ─── 5) Save pages to PNG and collect paths ───
        paths: List[str] = []
        for idx, img in enumerate(images):
            # Use a more accessible temp directory on Windows
            temp_dir = os.environ.get("TEMP", "C:\\Windows\\Temp")
            out_path = os.path.join(temp_dir, f"pdf_page_{idx+1}.png")
            img.save(out_path, "PNG")
            paths.append(out_path)

        self.status = f"Erzeugt {len(paths)} Seitenbilder"
        return Data(data={"image_paths": paths})
