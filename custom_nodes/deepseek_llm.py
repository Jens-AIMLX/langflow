from langflow.interface.custom import register_llm

@register_llm(
    name="DeepSeek Local",
    type="llm",
    parameters={
        "base_url": {"type": "string", "default": "http://host.docker.internal:8000"}
    },
)
class DeepSeekLLM:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt, max_tokens=512, temperature=0.7):
        import requests
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        resp = requests.post(f"{self.base_url}/v1/generate", json=payload)
        resp.raise_for_status()
        return resp.json()["text"]
