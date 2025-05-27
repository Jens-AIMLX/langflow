# custom_nodes/tesseract_local_ocr.py

from typing import List, Any, Tuple
from langflow.custom import Component
from langflow.io import DataInput, Output
from langflow.schema import Data
from PIL import Image, ImageFilter
import pytesseract
import os
import sys
import subprocess
import traceback

class TesseractLocalOCR(Component):
    """
    Extract text from image files (PNGs) using pytesseract,
    with simple logging helpers baked in.
    """
    display_name = "Tesseract OCR (Local)"
    name = "TesseractLocalOCR"
    description = "Runs pytesseract on each PNG (preprocessed) and concatenates the results."
    icon = "text"

    inputs = [
        DataInput(
            name="file_data",
            display_name="File Data",
            info="Data output from PdfToImagesComponent (unwraps image_paths).",
            dynamic=True,
            show=True,
        ),
    ]
    outputs = [
        Output(
            name="ocr_text",
            display_name="Extracted Text",
            method="extract_text",
            info="All page texts joined together.",
        ),
    ]

    def log_info(self, msg: str):
        print(f"[TesseractLocalOCR INFO] {msg}")

    def log_error(self, msg: str):
        print(f"[TesseractLocalOCR ERROR] {msg}")
        
    def find_tesseract_in_common_locations(self):
        """Try to find Tesseract in common installation locations"""
        potential_locations = [
            # Project-specific installations
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                        "langflow_venv", "tesseract", "tesseract.exe"),
            # Standard installations
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.join(os.environ.get("APPDATA", ""), "Local", "Programs", "Tesseract-OCR", "tesseract.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Tesseract-OCR", "tesseract.exe"),
        ]
        
        # Check the path environment variable
        for path_dir in os.environ.get('PATH', '').split(os.pathsep):
            potential_locations.append(os.path.join(path_dir, "tesseract.exe"))
        
        for location in potential_locations:
            if os.path.isfile(location):
                self.log_info(f"Found Tesseract at: {location}")
                return location
                
        return None
        
    def check_tesseract_installation(self):
        """Check if Tesseract is installed and in PATH, return diagnostic info"""
        try:
            # First, try to find Tesseract in common locations
            tesseract_path = self.find_tesseract_in_common_locations()
            if tesseract_path:
                # Set the tesseract command to the found path
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                
            # Check if pytesseract can find the tesseract executable
            tesseract_cmd = pytesseract.pytesseract.tesseract_cmd
            self.log_info(f"Tesseract command: {tesseract_cmd}")
            
            # Check if the file exists
            if not os.path.exists(tesseract_cmd):
                self.log_error(f"Tesseract executable not found at: {tesseract_cmd}")
                return False, f"Tesseract executable not found at: {tesseract_cmd}"
            
            # Try running tesseract version command
            try:
                result = subprocess.run([tesseract_cmd, "--version"], 
                                       capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log_info(f"Tesseract version: {result.stdout.splitlines()[0]}")
                    return True, "Tesseract is properly installed."
                else:
                    self.log_error(f"Tesseract command failed: {result.stderr}")
                    return False, f"Tesseract failed: {result.stderr}"
            except subprocess.SubprocessError as e:
                self.log_error(f"Error executing Tesseract: {e}")
                return False, f"Error executing Tesseract: {e}"
            
        except FileNotFoundError:
            self.log_error("Tesseract executable not found in PATH")
            return False, "Tesseract executable not found in PATH"
        except Exception as e:
            self.log_error(f"Error checking Tesseract: {e}")
            self.log_error(traceback.format_exc())
            return False, f"Error checking Tesseract: {e}"
            
    def extract_text(self) -> Data:
        # Check Tesseract installation
        tesseract_ok, tesseract_msg = self.check_tesseract_installation()
        if not tesseract_ok:
            # Try to set tesseract command based on common locations
            potential_paths = [
                os.path.join(os.environ.get("VIRTUAL_ENV", ""), "tesseract", "tesseract.exe"),
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                            "langflow_venv", "tesseract", "tesseract.exe"),
                os.path.join(os.environ.get("APPDATA", ""), "Local", "Programs", "Tesseract-OCR", "tesseract.exe"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Tesseract-OCR", "tesseract.exe"),
            ]
            
            for path in potential_paths:
                if os.path.exists(path):
                    self.log_info(f"Found Tesseract at: {path}")
                    pytesseract.pytesseract.tesseract_cmd = path
                    tesseract_ok = True
                    break
                    
        # Print environment variables that might affect Tesseract
        self.log_info(f"PATH: {os.environ.get('PATH', '')}")
        self.log_info(f"TESSDATA_PREFIX: {os.environ.get('TESSDATA_PREFIX', '')}")
        
        # 1) Unwrap DataInput into raw_paths list
        raw_paths: List[str] = []
        for item in (self.file_data or []):
            try:
                # DataInput sometimes gives Data instances, sometimes (key,value) tuples
                if isinstance(item, tuple) and len(item) == 2:
                    data_dict = item[1]
                elif hasattr(item, "data"):
                    data_dict = item.data
                else:
                    self.log_error(f"Unrecognized item in file_data: {item!r}")
                    continue
                pages = data_dict.get("image_paths", [])
                if isinstance(pages, list):
                    raw_paths.extend(pages)
            except Exception as e:
                self.log_error(f"Failed to unwrap file_data entry: {e}")

        self.log_info(f"OCR will process {len(raw_paths)} images: {raw_paths}")

        # 2) Loop, preprocess, OCR
        texts: List[str] = []
        for path in raw_paths:
            try:
                self.log_info(f"Opening image: {path}")
                img = Image.open(path)

                self.log_info("  → to grayscale")
                img = img.convert("L")

                self.log_info("  → unsharp mask")
                img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

                self.log_info("  → binary threshold")
                img = img.point(lambda p: 255 if p > 150 else 0)

                self.log_info("  → resize 1.5×")
                w, h = img.size
                img = img.resize((int(w * 1.5), int(h * 1.5)), Image.BICUBIC)

                self.log_info("  → running OCR")
                # Add tesseract command explicit setting to diagnose issues
                if not tesseract_ok:
                    err_msg = f"Tesseract is not installed or not in PATH. {tesseract_msg}"
                    self.log_error(err_msg)
                    texts.append(f"[Error reading {path}: {err_msg}]")
                    continue
                
                # Find TESSDATA_PREFIX if not set
                if not os.environ.get('TESSDATA_PREFIX'):
                    tesseract_dir = os.path.dirname(pytesseract.pytesseract.tesseract_cmd)
                    potential_tessdata_paths = [
                        os.path.join(tesseract_dir, "tessdata"),
                        os.path.join(os.path.dirname(tesseract_dir), "tessdata"),
                        os.path.join(os.path.dirname(os.path.dirname(tesseract_dir)), "tessdata"),
                    ]
                    for tess_path in potential_tessdata_paths:
                        if os.path.exists(tess_path) and os.path.isdir(tess_path):
                            os.environ['TESSDATA_PREFIX'] = tess_path
                            self.log_info(f"Setting TESSDATA_PREFIX to {tess_path}")
                            break
                
                # Explicitly state language and config
                try:
                    txt = pytesseract.image_to_string(img, lang="deu", config="--psm 3")
                except pytesseract.TesseractNotFoundError:
                    self.log_error("Tesseract not found when executing OCR")
                    texts.append(f"[Error reading {path}: Tesseract not found when executing OCR]")
                    continue
                except Exception as e:
                    self.log_error(f"OCR error: {e}")
                    if "not found" in str(e).lower() or "language" in str(e).lower():
                        # Try without language specification
                        self.log_info("Trying OCR without language specification")
                        try:
                            txt = pytesseract.image_to_string(img, config="--psm 3")
                        except Exception as e2:
                            self.log_error(f"Second OCR error: {e2}")
                            texts.append(f"[Error reading {path}: {e2}]")
                            continue
                    else:
                        texts.append(f"[Error reading {path}: {e}]")
                        continue
                        
                cleaned = txt.strip()
                self.log_info(f"    OCR result (first 100 chars): {cleaned[:100]!r}")
                texts.append(cleaned)

            except Exception as e:
                self.log_error(f"Error on {path}: {e}")
                self.log_error(traceback.format_exc())
                texts.append(f"[Error reading {path}: {e}]")

        result = "\n\n".join(texts)
        self.log_info(f"Final OCR text length: {len(result)}")
        return Data(data={"ocr_text": result})
