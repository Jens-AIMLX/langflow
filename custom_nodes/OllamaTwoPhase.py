# File: twophase_ollama.py
from langflow.custom import Component
from langflow.io import MessageTextInput, TextInput, Output
from langflow.schema import Data
import requests

class TwoPhaseOllama(Component):
    display_name = "Two‐Phase Ollama"
    name = "TwoPhaseOllama"
    description = "Run a two‐step extract+compose flow against one Ollama server."
    icon = "layers"  # any lucide icon

    inputs = [
        TextInput(
            name="pdf_text",
            display_name="PDF Text",
            info="Raw text extracted from your PDF",
            value="(your PDF here)",
        ),
        TextInput(
            name="rtf_text",
            display_name="RTF Text",
            info="Raw text from the RTF",
            value="(your RTF here)",
        ),
        MessageTextInput(
            name="template_prompt",
            display_name="First‐Phase Prompt",
            info="How to extract the table/data first",
            value="Extract the key table from the PDF text above as JSON...",
            tool_mode=True,
        ),
        MessageTextInput(
            name="compose_prompt",
            display_name="Second‐Phase Prompt",
            info="How to combine extracted data + full PDF/RTF into final result",
            value="Using the extracted JSON table plus PDF/RTF, write me a summary...",
            tool_mode=True,
        ),
        TextInput(
            name="base_url",
            display_name="Ollama Base URL",
            info="e.g. http://host.docker.internal:11434",
            value="http://host.docker.internal:11434",
        ),
        TextInput(
            name="model",
            display_name="Model Name",
            info="Which Ollama model to invoke (leave blank for default)",
            value="",
        ),
        TextInput(
            name="max_tokens",
            display_name="Max Tokens",
            info="Tokens per call",
            value="512",
        ),
        TextInput(
            name="temperature",
            display_name="Temperature",
            info="Sampling temperature",
            value="0.7",
        ),
    ]

    outputs = [
        Output(display_name="Final Response", name="response", method="build_output"),
    ]

    def build_output(self) -> Data:
        # Helper to call /api/generate
        def call_ollama(prompt: str) -> str:
            url = self.base_url.rstrip("/") + "/api/generate"
            payload = {
                "model": self.model or None,
                "prompt": prompt,
                "max_tokens": int(self.max_tokens),
                "temperature": float(self.temperature),
            }
            r = requests.post(url, json=payload, timeout=30)
            r.raise_for_status()
            return r.json().get("response", "")

        # 1) Extract step
        extracted = call_ollama(self.template_prompt + "\n\nPDF:\n" + self.pdf_text)

        # 2) Compose step, feeding in extracted + full context
        final_prompt = (
            f"Here is the extracted table/data:\n{extracted}\n\n"
            f"Full PDF text:\n{self.pdf_text}\n\n"
            f"Full RTF text:\n{self.rtf_text}\n\n"
            f"{self.compose_prompt}"
        )
        final_text = call_ollama(final_prompt)

        out = Data(value=final_text)
        self.status = out
        return out
