# 3. LangChain/LangGraph Integration mit Cursor (ohne OpenAI-API, nur mit lokalem LLM)

## Step-by-Step-Setup (komplett lokal, kein OpenAI-Schlüssel nötig)

### 1. Lokales LLM bereitstellen (z.B. mit Ollama)

- Installiere Ollama: [https://ollama.com/download](https://ollama.com/download)
- Lade ein beliebiges Modell (z.B. Mistral, Llama 3, Codellama, Phi3):

  ```bash
  ollama pull mistral
  ollama run mistral
  ```

- Alternativ: LM Studio, LocalAI, vllm, llama.cpp etc.

### 2. LangChain/LangGraph Agent mit lokalem LLM aufsetzen

**Beispiel mit Ollama als Backend:**

```python
# pip install langchain langgraph fastapi uvicorn
from fastapi import FastAPI, Request
from langchain.llms import Ollama
from langchain.chains import LLMChain

app = FastAPI()
llm = Ollama(model="mistral")
qa_chain = LLMChain(llm=llm, prompt="Beantworte die folgende Frage:" )

@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    frage = data["question"]
    antwort = qa_chain.run(frage)
    return {"answer": antwort}
```

- Server starten:

  ```bash
  uvicorn deine_datei:app --reload --port 8000
  ```

- **Kein OpenAI-API-Key nötig!**

### 3. In Cursor Plugin/Skript zum lokalen LangChain-Agent

```python
import requests

def ask_langchain(question):
    url = "http://localhost:8000/ask"
    data = {"question": question}
    response = requests.post(url, json=data)
    if response.ok:
        return response.json()["answer"]
    else:
        return response.text

if __name__ == "__main__":
    print(ask_langchain("Welche Bugs wurden im letzten Commit gelöst?"))
```

---

## Use Case: Knowledge-Graph-Fragen aus Cursor heraus (rein lokal)

1. User fragt im Editor z.B. "Welche Tests sind fehlgeschlagen?" via Plugin/Snippet.
2. Das Plugin sendet die Frage an die Knowledge-Agent-API (LangChain/LangGraph mit lokalem LLM).
3. Der Agent verarbeitet die Frage und durchsucht z.B. eine lokale Knowledge Base.
4. Die Antwort erscheint im Editor als Kommentar, Output oder neue Datei.

---

## Hinweise

- Du kannst beliebige lokale LLMs als Backend verwenden (siehe LangChain-Provider)
- **Kein OpenAI-API-Key oder Fremdserver nötig!**
- Authentifizierung und Sicherheit bei API-Servern beachten
- Performance hängt von Hardware und Modell ab
