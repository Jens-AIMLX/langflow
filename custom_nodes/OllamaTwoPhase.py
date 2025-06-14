from typing import Any
from urllib.parse import urljoin
import httpx
from langflow.custom import Component
from langflow.inputs import StrInput, MultilineInput
from langflow.io import DropdownInput, Output
from langflow.schema import Data
from langflow.base.models.ollama_constants import OLLAMA_EMBEDDING_MODELS, OLLAMA_TOOL_MODELS_BASE, URL_LIST
import requests

HTTP_STATUS_OK = 200

class OllamaTwoPhase(Component):
    display_name = "Ollama Two-Phase"
    name = "OllamaTwoPhase"
    description = "1) Extract structured data, 2) Compose final answer with user query—all in one node."
    icon = "layers"

    inputs = [
        MultilineInput(
            name="pdf_text",
            display_name="PDF Text",
            info="OCR’d text from your PDF",
            value=""
        ),
        MultilineInput(
            name="rtf_text",
            display_name="RTF Text",
            info="Text extracted from your RTF/Word template",
            value=""
        ),
        MultilineInput(
            name="extract_prompt",
            display_name="Extract Prompt",
            info="Template prompt to pull structured data (e.g. JSON/table) from the PDF text",
            value="Extract the key table from the following PDF text as JSON…"
        ),
        MultilineInput(
            name="compose_prompt",
            display_name="Compose (System) Prompt",
            info="System‐style instructions for how to produce the final answer",
            value="Using the extracted data plus PDF/RTF content, create a comprehensive summary…"
        ),
        MultilineInput(
            name="chat_input",
            display_name="User Query",
            info="The user’s actual question or additional instructions",
            value=""
        ),
        StrInput(
            name="base_url",
            display_name="Ollama Base URL",
            info="e.g. http://localhost:11434 or http://127.0.0.1:11434",
            value="http://localhost:11434"
        ),
        DropdownInput(
            name="model_name",
            display_name="Model Name",
            info="Leave blank for Ollama’s default",
            options=[],
            refresh_button=True,
            real_time_refresh=True,
        ),
        StrInput(
            name="max_tokens",
            display_name="Max Tokens",
            info="Max tokens per call",
            value="512"
        ),
        StrInput(
            name="temperature",
            display_name="Temperature",
            info="Sampling temperature",
            value="0.7"
        ),
    ]

    outputs = [
        Output(display_name="Final Response", name="response", method="build_final_response"),
        Output(display_name="Phase 1 Extract", name="extracted_data", method="build_extracted_data"),
        Output(display_name="Phase 2 Prompt", name="final_prompt", method="build_final_prompt")
    ]

    async def is_valid_ollama_url(self, url: str) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                return (await client.get(urljoin(url, "api/tags"))).status_code == HTTP_STATUS_OK
        except httpx.RequestError:
            return False

    async def update_build_config(self, build_config: dict, field_value: Any, field_name: str | None = None):
        if field_name in {"base_url", "model_name"} and not await self.is_valid_ollama_url(
            build_config["base_url"].get("value", "")
        ):
            # Check if any URL in the list is valid
            valid_url = ""
            for url in URL_LIST:
                if await self.is_valid_ollama_url(url):
                    valid_url = url
                    break
            if valid_url != "":
                build_config["base_url"]["value"] = valid_url
            else:
                msg = "No valid Ollama URL found."
                raise ValueError(msg)

        if field_name in {"model_name", "base_url"}:
            if await self.is_valid_ollama_url(self.base_url):
                build_config["model_name"]["options"] = await self.get_model(self.base_url)
            elif await self.is_valid_ollama_url(build_config["base_url"].get("value", "")):
                build_config["model_name"]["options"] = await self.get_model(
                    build_config["base_url"].get("value", "")
                )
            else:
                build_config["model_name"]["options"] = []

        return build_config

    async def get_model(self, base_url_value: str) -> list[str]:
        try:
            url = urljoin(base_url_value, "api/tags")
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

            model_ids = [model["name"] for model in data.get("models", [])]
            # Filter out embedding models
            model_ids = [
                model
                for model in model_ids
                if not any(
                    model == embedding_model or model.startswith(embedding_model.split("-")[0])
                    for embedding_model in OLLAMA_EMBEDDING_MODELS
                )
            ]

        except (ImportError, ValueError, httpx.RequestError, Exception) as e:
            msg = "Could not get model names from Ollama."
            raise ValueError(msg) from e
        return model_ids

    def build_final_response(self) -> Data:
        """Main method that runs the two-phase process and returns the final response."""
        return self._run_two_phase_process()

    def build_extracted_data(self) -> Data:
        """Returns the extracted data from Phase 1."""
        self._run_two_phase_process()
        return Data(value=getattr(self, 'extracted_data_result', ''))

    def build_final_prompt(self) -> Data:
        """Returns the final prompt used in Phase 2."""
        self._run_two_phase_process()
        return Data(value=getattr(self, 'final_prompt_result', ''))

    def _run_two_phase_process(self) -> Data:
        base = self.base_url.rstrip("/")

        # Test connection to Ollama first
        try:
            test_resp = requests.get(f"{base}/api/tags", timeout=5)
            if test_resp.status_code != 200:
                self.status = f"Ollama server responded with status {test_resp.status_code}"
                return Data(value=f"Error: Ollama server at {base} responded with status {test_resp.status_code}")
        except requests.exceptions.ConnectionError:
            error_msg = f"Cannot connect to Ollama at {base}. Please ensure Ollama is running and accessible."
            if "host.docker.internal" in base:
                error_msg += " Note: 'host.docker.internal' only works inside Docker containers. Use 'localhost' or '127.0.0.1' for local installations."
            self.status = error_msg
            return Data(value=f"Error: {error_msg}")
        except Exception as e:
            error_msg = f"Error testing connection to Ollama: {str(e)}"
            self.status = error_msg
            return Data(value=f"Error: {error_msg}")

        def call_ollama(prompt: str) -> str:
            # Validate model is selected
            if not self.model_name:
                raise ValueError("Please select a model from the dropdown before running the component.")

            try:
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": int(self.max_tokens),
                        "temperature": float(self.temperature),
                    }
                }

                self.status = f"Calling Ollama with model: {self.model_name}"
                resp = requests.post(f"{base}/api/generate", json=payload, timeout=120)

                if resp.status_code == 500:
                    error_detail = resp.text if resp.text else "Internal server error"
                    raise ValueError(f"Ollama server error (500): {error_detail}. Try a different model or check Ollama logs.")

                resp.raise_for_status()

                # Parse response
                try:
                    response_data = resp.json()
                    if "error" in response_data:
                        raise ValueError(f"Ollama error: {response_data['error']}")
                    return response_data.get("response", "")
                except ValueError as e:
                    if "Ollama error:" in str(e):
                        raise e
                    # Handle potential streaming response
                    response_text = ""
                    for line in resp.text.strip().split('\n'):
                        if line.strip():
                            try:
                                import json
                                chunk = json.loads(line)
                                if isinstance(chunk, dict) and "response" in chunk:
                                    response_text += chunk["response"]
                            except json.JSONDecodeError:
                                continue
                    return response_text if response_text else resp.text

            except requests.exceptions.Timeout:
                raise TimeoutError(f"Ollama request timed out after 120 seconds. The model '{self.model_name}' might be too large or the prompt too complex.")
            except requests.exceptions.ConnectionError as e:
                error_msg = f"Cannot connect to Ollama at {base}. Please ensure Ollama is running and accessible."
                if "host.docker.internal" in base:
                    error_msg += " Note: 'host.docker.internal' only works inside Docker containers. Use 'localhost' or '127.0.0.1' for local installations."
                raise ConnectionError(error_msg) from e
            except requests.exceptions.RequestException as e:
                raise ConnectionError(f"Error communicating with Ollama at {base}: {str(e)}") from e

        try:
            # 1) Extract structured data from the PDF
            self.status = "Phase 1: Extracting structured data from PDF..."
            print(f"[OllamaTwoPhase] Phase 1: Extracting data using model {self.model_name}")
            extracted = call_ollama(
                f"{self.extract_prompt}\n\nPDF TEXT:\n{self.pdf_text}"
            )
            print(f"[OllamaTwoPhase] Phase 1 Result: {extracted[:200]}...")

            # 2) Compose final answer: include system instructions, user query, extracted data, and both docs
            self.status = "Phase 2: Composing final answer..."
            final_prompt = (
                f"{self.compose_prompt}\n\n"
                f"User Query:\n{self.chat_input}\n\n"
                f"Extracted Data:\n{extracted}\n\n"
                f"Full PDF Text:\n{self.pdf_text}\n\n"
                f"Full RTF Text:\n{self.rtf_text}"
            )
            print(f"[OllamaTwoPhase] Phase 2: Final prompt length: {len(final_prompt)} chars")
            final = call_ollama(final_prompt)
            print(f"[OllamaTwoPhase] Phase 2 Result: {final[:200]}...")

            self.status = "Done"

            # Store results for different outputs
            self.extracted_data_result = extracted
            self.final_prompt_result = final_prompt
            self.final_response_result = final

            # Return based on which output is being requested
            # This is a bit of a hack since Langflow doesn't have a clean way to handle multiple outputs
            # We'll return the final response by default
            return Data(value=final)

        except Exception as e:
            error_msg = f"Error in two-phase processing: {str(e)}"
            self.status = error_msg
            return Data(value=error_msg)
