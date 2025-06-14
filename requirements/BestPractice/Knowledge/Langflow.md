# 1. Langflow-Integration mit Cursor

## Step-by-Step-Setup

### 1. Langflow lokal als Server starten

- Installation:

  ```bash
  pip install langflow
  langflow run
  ```

- Standardmäßig läuft Langflow auf `http://localhost:7860`

### 2. In Langflow einen Flow bauen

- Erstelle z.B. einen QA-Flow oder einen Retrieval-Agenten
- Exportiere den Flow als API-Endpunkt (siehe Langflow Docs)

### 3. API-Endpoint in Cursor ansprechen

- Schreibe ein Skript oder ein Plugin, das Requests an Langflow sendet.

---

## Plugin-Vorlage (Python, für Cursor)

```python
import requests

def query_langflow(prompt):
    # Passe die URL ggf. auf deinen Flow an
    url = "http://localhost:7860/api/v1/predict"
    data = {"inputs": prompt}
    response = requests.post(url, json=data)
    if response.ok:
        return response.json()
    else:
        return response.text

# Beispiel-Aufruf
if __name__ == "__main__":
    frage = "Fasse das README zusammen."
    print(query_langflow(frage))
```

---

## Use Case: Automatische Projekt-Zusammenfassung

1. User markiert im Cursor-Editor den Text, wählt das Plugin "Langflow Summary".
2. Das Plugin schickt den Text an den Langflow-Endpunkt.
3. Langflow verarbeitet (z.B. mit LLM und RAG-Chain) und gibt die Zusammenfassung zurück.
4. Die Antwort wird als Kommentar oder neue Datei im Editor eingefügt.

---

## Hinweise

- Die API-Route und Payload kann je nach Flow-Export abweichen (siehe Langflow Docs)
- Sicherheit: Setze ggf. Authentifizierung für die API
- Erweiterbar für QA, Refactoring, Testmanagement usw.
