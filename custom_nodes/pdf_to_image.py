from typing import List
from langflow.custom import Component
from langflow.io import StrInput, Output
from langflow.schema import Data
from pdf2image import convert_from_path, convert_from_bytes

class PdfToImagesComponent(Component):
    """
    Convert each page of a PDF file into separate PNG image files.
    """
    display_name = "PDF to Images"
    name = "PdfToImagesComponent"
    description = "Wandelt jede Seite eines PDFs in ein PNG-Bild um."
    icon = "file-image"

    inputs = [
        StrInput(
            name="pdf_path",
            display_name="PDF Path",
            info="Lokaler Pfad zur PDF-Datei (z. B. vom File-Node).",
        ),
    ]

    outputs = [
        Output(
            name="image_paths",
            display_name="Image Paths",
            method="convert_pdf_to_images",
            info="Liste der Pfade zu den generierten PNG-Bildern",
        ),
    ]

    def convert_pdf_to_images(self) -> Data:
        pdf = self.pdf_path
        try:
            images = convert_from_path(pdf, dpi=300)
        except Exception:
            images = convert_from_bytes(pdf, dpi=300)

        paths: List[str] = []
        for idx, img in enumerate(images):
            out_path = f"/tmp/pdf_page_{idx+1}.png"
            img.save(out_path, "PNG")
            paths.append(out_path)

        self.status = f"Erzeugt {len(paths)} Seitenbilder"
        return Data(data={"image_paths": paths})
