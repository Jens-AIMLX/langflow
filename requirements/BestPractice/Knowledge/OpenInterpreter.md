# 2. Open Interpreter Integration mit Cursor

## Step-by-Step-Setup

### 1. Open Interpreter lokal als Server starten

- Installation:

  ```bash
  pip install open-interpreter
  open-interpreter --server --port 4000
  ```

- Standard-Port: `http://localhost:4000`

### 2. In Cursor ein Python-Skript/Plugin schreiben, das HTTP-Requests schickt

- Für Automatisierung, Testing, Terminal-Steuerung usw.

---

## Plugin-Vorlage (Python, für Cursor)

```python
import requests

def ask_open_interpreter(prompt):
    url = "http://localhost:4000/chat"
    data = {"messages": [{"role": "user", "content": prompt}]}
    response = requests.post(url, json=data)
    if response.ok:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return response.text

# Beispiel-Aufruf
if __name__ == "__main__":
    command = "Führe pytest aus und gib das Ergebnis aus."
    print(ask_open_interpreter(command))
```

---

## Use Case: Automatisiertes Testen und Reporting

1. User startet das Plugin "Run Tests with Open Interpreter" aus Cursor.
2. Das Plugin sendet den Befehl "Führe pytest aus" an Open Interpreter.
3. Open Interpreter führt die Tests im Terminal aus und sendet das Ergebnis zurück.
4. Das Plugin zeigt die Ergebnisse als Editor-Output oder als Kommentar an.

---

## Hinweise

- Open Interpreter kann beliebige Shell-/Python-Kommandos ausführen – Vorsicht bei kritischen Befehlen!
- Optional: Authentifizierung/Token für den Open Interpreter-Server einrichten
- Erweiterbar für Build, Lint, Refactoring, Knowledge-Tools usw.
