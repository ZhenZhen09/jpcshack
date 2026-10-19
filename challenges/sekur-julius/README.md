# Sekur Julius

The shared challenge service creates a fresh Caesar-shifted flag for each browser session and validates submissions on the server. Open the Challenge Index and select Sekur Julius; the local launcher starts the shared service on demand. On Ubuntu, Nginx serves this page and proxies its API to `ctf-mini-challenges.service`.