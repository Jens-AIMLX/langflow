# 3. LangChain/LangGraph Integration mit Cursor

## Step-by-Step-Setup

### 1. Knowledge-/QA-Agent als API-Server aufsetzen

- Beispiel mit FastAPI:

```python
# pip install langchain langgraph fastapi uvicorn
from fastapi import FastAPI, Request
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI  # Oder ein anderes LLM
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

app = FastAPI()
vectorstore = FAISS.load_local("pfad/zu/vectordb", OpenAIEmbeddings())
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

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

### 2. In Cursor ein Plugin/Skript zum Anfragen der API

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

# Beispiel
if __name__ == "__main__":
    print(ask_langchain("Welche Bugs wurden im letzten Commit gelöst?"))
```

---

## Use Case: Knowledge-Graph-Fragen aus Cursor heraus stellen

1. User fragt im Editor z.B. "Welche Tests sind fehlgeschlagen?" via Plugin/Snippet.
2. Das Plugin sendet die Frage an die Knowledge-Agent-API (LangChain/LangGraph).
3. Der Agent durchsucht Knowledge Base, Code, Issues, Testdaten usw.
4. Die Antwort erscheint im Editor als Kommentar, Output oder neue Datei.

---

## Hinweise

- Für LangGraph siehe [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- Agenten können beliebig erweitert werden (Testmanagement, Refactoring, Taskmanagement)
- Sicherheit (z.B. API-Schutz) beachten, besonders bei Remote-Servern
