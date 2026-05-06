import urllib.request
import json
import os

LMSTUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL = "google/gemma-4-e4b"

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "Eres un asistente."},
        {"role": "user", "content": "Hola, responde con una sola palabra: OK."}
    ],
    "temperature": 0.1
}

print(f"Probando conexión a: {LMSTUDIO_URL}")
print(f"Modelo: {MODEL}")

try:
    req = urllib.request.Request(
        LMSTUDIO_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
        print("\n--- RESPUESTA ---")
        print(result["choices"][0]["message"]["content"])
        print("\n¡CONEXIÓN EXITOSA!")

except Exception as e:
    print(f"\n❌ ERROR DE CONEXIÓN: {e}")
