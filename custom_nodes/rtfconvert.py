from langflow.custom import Component
from langflow.io import FileInput, BoolInput, Output
from langflow.schema import Message
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.plaintext.writer import PlaintextWriter
import os
import asyncio


# Remove the custom FileInput class since Pydantic validation prevents custom attributes





class RTFParserComponent(Component):
    display_name = "RTF Document Parser"
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

    def get_original_filename_sync(self, file_path: str) -> str:
        """Get the original filename using the DEFINITIVE strategy."""

        print(f"[RTF Parser] === DEFINITIVE FILENAME LOOKUP ===")
        print(f"File path received: {file_path}")

        # DEFINITIVE STRATEGY: Access _inputs['rtf_file'].value
        # Based on comprehensive testing, this is where the original filename is stored
        try:
            if hasattr(self, '_inputs') and 'rtf_file' in self._inputs:
                rtf_input = self._inputs['rtf_file']
                print(f"[RTF Parser] Found _inputs['rtf_file']: {rtf_input}")

                if hasattr(rtf_input, 'value') and rtf_input.value:
                    original_filename = rtf_input.value
                    print(f"[RTF Parser] _inputs['rtf_file'].value = {original_filename}")

                    # Check if this looks like an original filename (not a path)
                    if not ('/' in original_filename or '\\' in original_filename or len(original_filename) > 100):
                        print(f"[RTF Parser] ✅ SUCCESS! Using original filename: {original_filename}")
                        return original_filename
                    else:
                        print(f"[RTF Parser] ❌ Value looks like a path, not original filename")
                else:
                    print(f"[RTF Parser] ❌ No value property or value is empty")
            else:
                print(f"[RTF Parser] ❌ No _inputs or rtf_file not found")
        except Exception as e:
            print(f"[RTF Parser] ❌ Error accessing _inputs: {e}")

        # Fallback: Try database lookup
        print(f"[RTF Parser] Falling back to database lookup...")
        try:
            from pathlib import Path
            import sqlite3

            path_obj = Path(file_path)
            if len(path_obj.parts) >= 2:
                relative_path = f"{path_obj.parts[-2]}/{path_obj.parts[-1]}"
                print(f"[RTF Parser] Extracted relative path: {relative_path}")

                db_paths = [
                    "langflow.db",
                    os.path.expanduser("~/.langflow/langflow.db"),
                    os.path.join(os.getcwd(), "langflow.db")
                ]

                for db_path in db_paths:
                    if os.path.exists(db_path):
                        print(f"[RTF Parser] Found database at: {db_path}")
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT name FROM file WHERE path = ?", (relative_path,))
                        result = cursor.fetchone()
                        conn.close()

                        if result:
                            original_filename = result[0]
                            print(f"[RTF Parser] ✅ Found in database: {original_filename}")
                            return original_filename

        except Exception as e:
            print(f"[RTF Parser] Database lookup failed: {e}")

        # Final fallback
        basename = os.path.basename(file_path)
        print(f"[RTF Parser] ❌ Using fallback basename: {basename}")
        return basename

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

            # Get the original filename using multiple strategies
            filename = self.get_original_filename_sync(file_path)

            # Add filename as first line
            final_text = f"File: {filename}\n\n{text}"

            self.status = f"RTF parsed successfully. Extracted {len(text)} characters from {filename}."

            # Return as Message object
            return Message(
                text=final_text,
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