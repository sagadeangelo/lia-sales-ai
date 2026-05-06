import json
import urllib.request
import os

from config.precios import PRODUCTOS
from crm.manager import update_lead, register_sale
from response_engine import detect_intent, get_template_response

# CONFIGURACIÓN IA (LM STUDIO / OLLAMA)
BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:1234")
MODEL = os.getenv("OLLAMA_MODEL", "google/gemma-4-e4b")
LMSTUDIO_URL = f"{BASE_URL}/v1/chat/completions"

FAST_PROMPT = """
Eres LIA.
Responde corto, útil y humano.
Máximo 60 palabras.
"""

def is_fast_message(message):
    msg = message.lower()

    simple_patterns = [
        "hola",
        "precio",
        "informacion",
        "información",
        "quiero saber",
        "me interesa",
        "que incluye",
        "cómo funciona",
        "simulador",
        "ia",
        "libros",
        "egel"
    ]

    return (
        len(msg.split()) <= 12
        or any(p in msg for p in simple_patterns)
    )

class LocalAgent:
    def __init__(self, name, prompt_path):
        self.name = name
        self.prompt_path = prompt_path
        self.prompt = self._load_prompt()

    def _load_prompt(self):
        if os.path.exists(self.prompt_path):
            with open(self.prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        return f"Eres el agente {self.name}. Responde profesionalmente."

    def run(self, message: str, session: dict, system_override: str = None):
        import time
        import random
        start = time.time()

        fallbacks = [
            "¡Claro! 😊 Cuéntame qué te interesa más.",
            "Sí 😊 puedo ayudarte con eso.",
            "¡Va! ⚡ Te explico rapidísimo.",
            "¡Hola! 👋 Soy LIA. ¿Te interesa el simulador EGEL o herramientas IA?"
        ]

        system_content = system_override if system_override else self.prompt
        
        messages = [{"role": "system", "content": system_content}]
        # SOLO últimos 4 mensajes del historial para performance
        history = session.get("history", [])[-4:]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        payload = {
            "model": MODEL,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 80,
            "stop": ["</s>", "USER:", "ASSISTANT:"]
        }

        try:
            req = urllib.request.Request(
                LMSTUDIO_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )

            # Gemma optimizada: 30s timeout para arquitectura híbrida
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                if "choices" not in result or not result["choices"]:
                    print("[ERROR LM] respuesta inválida:", result)
                    return random.choice(fallbacks)

                content = result["choices"][0]["message"]["content"].strip()
                elapsed = time.time() - start
                print(f"⚡ Tiempo total LM: {elapsed:.2f}s")
                
                if not content:
                    print("[ERROR LM] respuesta vacía detectada")
                    return random.choice(fallbacks)

                return content

        except Exception as e:
            print(f"[ERROR AGENTE {self.name}]:", e)
            return random.choice(fallbacks)


# =========================
# PARSER
# =========================

def parse_strategic_json(response: str):
    try:
        # Intentar encontrar JSON en el texto si hay ruido
        if "{" in response and "}" in response:
            start = response.find("{")
            end = response.rfind("}") + 1
            json_str = response[start:end]
            return json.loads(json_str)
        return {}
    except:
        return {}


# =========================
# DETECCIÓN
# =========================

def detectar_carrera(message):
    msg = message.lower()

    if "derecho" in msg:
        return "Derecho"
    if "administracion" in msg or "admin" in msg:
        return "Administración"
    if "contaduria" in msg or "contabilidad" in msg:
        return "Contaduría"

    return None


def detectar_intencion(message):
    msg = message.lower()

    if any(x in msg for x in ["comprar", "pagar", "lo quiero", "donde compro"]):
        return "compra"

    if any(x in msg for x in ["precio", "cuanto cuesta", "costo"]):
        return "precio"

    if any(x in msg for x in ["interesado", "me interesa"]):
        return "interes"

    return None


# =========================
# PIPELINE HÍBRIDO
# =========================

def run_pipeline(session_id: str, session: dict, message: str):
    import time
    start_total = time.time()
    
    session.setdefault("history", [])
    contexto = session.get("contexto", "general")
    etapa = session.get("etapa", "captura")
    
    # 1. ROUTER (Rápido)
    intent = detect_intent(message)
    print(f"\n[ROUTER] Intent: {intent} | Contexto: {contexto}")

    # 2. AGENTE ESTRATÉGICO (IA Análisis)
    agente_actual_id = session.get("agente_actual", "agente_1")
    agents_map = {
        "agente_1": agente_1,
        "agente_2": agente_2,
        "agente_3": agente_3
    }
    agente_estrat = agents_map.get(agente_actual_id, agente_1)
    
    print(f"[STRATEGY] Analizando con {agente_estrat.name}...")
    strategy_raw = agente_estrat.run(message, session)
    strategy_data = parse_strategic_json(strategy_raw)
    
    # Actualizar estado desde estrategia
    detected_intent = strategy_data.get("intent", intent)
    lead_stage = strategy_data.get("lead_stage", etapa)
    next_action = strategy_data.get("next_action", "")
    response_type = strategy_data.get("response_type", "template")
    
    if strategy_data.get("detected_context"):
        session["contexto"] = strategy_data.get("detected_context")
        contexto = session["contexto"]

    session["etapa"] = lead_stage
    print(f"[STATE] Stage: {lead_stage} | Intent: {detected_intent} | Next: {next_action}")

    # 3. RESPONSE GENERATION (Template vs Fast IA)
    clean_msg = ""
    
    if response_type == "template":
        print("[RESPONSE] Usando Template...")
        clean_msg = get_template_response(detected_intent, contexto)
    else:
        print("[RESPONSE] Generando Fast IA...")
        clean_msg = agente_estrat.run(message, session, system_override=FAST_PROMPT)

    # Fallback si por algo queda vacío
    if not clean_msg or len(clean_msg.strip()) < 2:
        clean_msg = get_template_response("fallback", contexto)

    # ===== LEAD SCORING (Lógica Simplificada) =====
    score = session.get("lead_score", 0)
    if "pricing" in detected_intent: score += 2
    if "urgency" in detected_intent: score += 3
    if lead_stage == "warm": score += 2
    if lead_stage == "hot": score += 5
    session["lead_score"] = score
    session["lead_nivel"] = "HOT" if score >= 7 else "WARM" if score >= 4 else "COLD"

    # ===== CRM UPDATE =====
    update_lead(session_id, {
        "etapa": lead_stage,
        "lead_score": score,
        "lead_nivel": session["lead_nivel"],
        "ultimo_contexto": contexto
    })

    # ===== HISTORIAL =====
    session["history"].append({"role": "user", "content": message})
    session["history"].append({"role": "assistant", "content": clean_msg})
    if len(session["history"]) > 6:
        session["history"] = session["history"][-6:]

    elapsed_total = time.time() - start_total
    print(f"⚡ Tiempo Total Pipeline: {elapsed_total:.2f}s")
    
    return clean_msg


# =========================
# AGENTES ESTRATÉGICOS
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "agentes", "prompts"))

agente_1 = LocalAgent("agente_1", os.path.join(PROMPTS_DIR, "agente_1_estrategico.md"))
agente_2 = LocalAgent("agente_2", os.path.join(PROMPTS_DIR, "agente_2_estrategico.md"))
agente_3 = LocalAgent("agente_3", os.path.join(PROMPTS_DIR, "agente_3_estrategico.md"))