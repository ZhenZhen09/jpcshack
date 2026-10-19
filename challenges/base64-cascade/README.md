# Base64 Cascade

The shared challenge service creates a fresh flag, encodes it through two Base64 layers, and validates submissions on the server. Open the Challenge Index and select Base64 Cascade; the local launcher starts the shared service on demand. On Ubuntu, Nginx serves this page and proxies its API to `ctf-mini-challenges.service`.