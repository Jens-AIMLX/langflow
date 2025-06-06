# Ollama LLM Webservice für Internet-Zugriff – Setup und Sicherheit

## 1. Ziel

Ein Ollama-LLM, das lokal läuft, soll **nicht nur im Intranet**, sondern **aus dem Internet** per Webservice erreichbar sein. Beispiel: Zugriff von externen Tools, Clouds oder von unterwegs.

---

## 2. Grundlagen: Ollama-API öffentlich machen

Ollama bietet standardmäßig eine REST-API ([http://localhost:11434](http://localhost:11434)), aber **nur auf localhost** (127.0.0.1). Damit ist die API von außen nicht direkt erreichbar.

### Lösungsmöglichkeiten:

1. **Ollama auf eine öffentliche Netzwerkschnittstelle binden**
2. **Reverse Proxy (z.B. mit nginx oder Caddy) nutzen**
3. **Port-Forwarding/Firewall konfigurieren**
4. **SSL/TLS und Authentifizierung einrichten**

---

## 3. Step-by-Step: Ollama im Internet erreichbar machen

### Schritt 1: Reverse Proxy einrichten (empfohlen)

**Beispiel mit nginx:**

```nginx
server {
    listen 80;
    server_name deine-domain.de;

    location / {
        proxy_pass http://localhost:11434/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

- Mit Let’s Encrypt kannst du kostenlos SSL aktivieren: [Certbot Guide](https://certbot.eff.org/instructions)

### Schritt 2: Firewall & Port Forwarding

- Öffne Port 80 (http) und/oder 443 (https) in deiner Firewall/Router
- Leite Zugriffe an den Server mit nginx weiter

### Schritt 3: Optional – Ollama-API direkt auf 0.0.0.0 starten

- Standardmäßig geht das nicht per CLI, aber du kannst ein SSH-Tunnel nutzen oder ein API-Gateway davor setzen

### Schritt 4: Authentifizierung/Sicherheit

- **Sehr wichtig:** Eine offene LLM-API im Internet kann missbraucht werden! Setze IMMER Authentifizierung davor.
- Lösungsmöglichkeiten:

  - HTTP Basic Auth in nginx
  - JWT-Token-Verifizierung
  - API-Keys via Reverse Proxy (z.B. mit nginx-lua)

---

## 4. Beispiel: nginx mit Basic Auth

1. Passwort-Datei generieren:

   ```bash
   sudo apt install apache2-utils
   htpasswd -c /etc/nginx/.htpasswd user1
   ```

2. nginx-Konfiguration ergänzen:

   ```nginx
   location / {
       auth_basic "Ollama Secure";
       auth_basic_user_file /etc/nginx/.htpasswd;
       proxy_pass http://localhost:11434/;
       ...
   }
   ```

---

## 5. Wichtige Sicherheitstipps

- **Niemals** ein LLM ungeschützt ins Internet stellen!
- SSL (https) ist Pflicht
- Zugang begrenzen (IP-Whitelist, 2FA, etc. möglich)
- Optional: Rate Limiting in nginx aktivieren
- Bei Bedarf Monitoring/Logging einschalten

---

## 6. Weitere Hinweise

- Viele Anbieter nutzen Cloudflare Tunnel oder Zero Trust Proxy für zusätzliche Sicherheit
- Für produktive Nutzung lohnt sich evtl. eine Kubernetes/API Gateway-Lösung mit Auth, Logging etc.

---

## 7. Ressourcen

- [Ollama API Docs](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [nginx Doku](https://nginx.org/en/docs/)
- [Certbot Doku für SSL](https://certbot.eff.org/instructions)
- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)

---

**Fragen zum Setup? Willst du ein Beispiel für Caddy, Traefik, Docker, SSH-Tunnel? Sag Bescheid!**
