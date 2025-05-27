from typing import Optional
from langflow.custom import Component
from langflow.io import FileInput, BoolInput, Output
from langflow.schema import Message
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.plaintext.writer import PlaintextWriter
import os

class RTFParserComponent(Component):
    display_name = "RTF Parser"
    description = "Parse RTF documents and extract plain text content"
    icon = "file-text"
    name = "RTFParser"

    inputs = [
        FileInput(
            name="rtf_file",
            display_name="RTF File",
            info="Upload an RTF file to parse",
            file_types=["rtf"],
            required=True,
        ),
        BoolInput(
            name="preserve_formatting",
            display_name="Preserve Formatting",
            info="Whether to preserve basic formatting (like line breaks)",
            value=False,
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Parsed Text", name="parsed_text", method="parse_rtf"),
    ]

    def parse_rtf(self) -> Message:
        try:
            # Get the uploaded file path
            file_path = self.rtf_file

            if not file_path:
                raise ValueError("No RTF file provided")

            if not os.path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")

            # Read the RTF file in binary mode for pyth
            with open(file_path, 'rb') as file:
                doc = Rtf15Reader.read(file)

            # Convert to plain text using pyth
            if self.preserve_formatting:
                # Extract text while preserving some structure
                text_parts = []
                for element in doc.content:
                    if hasattr(element, 'content'):
                        text_parts.append(str(element.content))
                    else:
                        text_parts.append(str(element))
                text = '\n'.join(text_parts)
            else:
                # Convert to plain text without formatting
                text = PlaintextWriter.write(doc).getvalue()

            self.status = f"RTF parsed successfully. Extracted {len(text)} characters."

            # Return as Message object
            return Message(
                text=text,
                sender="RTF Parser",
                sender_name="RTF Parser Component"
            )

        except Exception as e:
            error_msg = f"Error parsing RTF: {str(e)}"
            self.status = error_msg
            return Message(
                text=error_msg,
                sender="RTF Parser",
                sender_name="RTF Parser Component"
            )