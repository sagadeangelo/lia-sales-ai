import json
import urllib.request
import os

from config.precios import PRODUCTOS
from crm.manager import update_lead, register_sale
from response_engine import detect_intent, get_template_response, detect_career, STRONG_INTENTS
from sales_flows import advance_flow

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
# PIPELINE HÍBRIDO
# =========================

def run_pipeline(session_id: str, session: dict, message: str):
    import time
    start_total = time.time()
    
    # === INITIALIZATION & SAFETY GUARDS ===
    session.setdefault("history", [])
    session.setdefault("sales_stage", "idle")
    session.setdefault("contexto", "general")
    
    contexto = session.get("contexto", "general")
    career = session.get("career")
    intent = detect_intent(message) or "general"
    current_stage = session.get("sales_stage", "idle")

    print(f"\n[CTX ACTIVE] {contexto}")
    print(f"[INTENT ACTIVE] {intent}")

    try:
        # 1. SOFT MEMORY / INTENT OVERRIDE
        # Si detectamos un intent FUERTE que no coincide con el contexto actual, cambiamos.
        if intent in STRONG_INTENTS:
            if "egel" in intent and contexto != "egel":
                print(f"[OVERRIDE] Usuario cambió a EGEL. Reseteando flow.")
                contexto = "egel"
                session["contexto"] = "egel"
                session["sales_stage"] = "idle" 
                current_stage = "idle"
            elif "lia" in intent and contexto != "lia_staylo":
                print(f"[OVERRIDE] Usuario cambió a LIA. Reseteando flow.")
                contexto = "lia_staylo"
                session["contexto"] = "lia_staylo"
                session["career"] = None 
                session["sales_stage"] = "idle"
                current_stage = "idle"
                career = None

        # 2. ROUTER - Carrera (Sticky Context mejorado)
        new_career = detect_career(message)
        if new_career:
            session["career"] = new_career
            session["contexto"] = "egel"
            contexto = "egel"
            career = new_career
            print(f"[CAREER] Nueva detección: {new_career} -> Forzando contexto EGEL")
        else:
            # Sticky Context: Mantener carrera si ya existe y seguimos en EGEL
            if contexto == "egel":
                career = session.get("career")
                if career:
                    print(f"[STICKY] Manteniendo Carrera: {career}")

        # 3. AGENTE ESTRATÉGICO (Análisis comercial con Memoria)
        agente_actual_id = session.get("agente_actual", "agente_1")
        agents_map = {
            "agente_1": agente_1,
            "agente_2": agente_2,
            "agente_3": agente_3
        }
        agente_estrat = agents_map.get(agente_actual_id, agente_1)
        
        # Inyectar estado en el prompt del agente
        prompt_con_estado = agente_estrat.prompt.replace("[PRODUCTO_ACTIVO]", contexto)
        prompt_con_estado = prompt_con_estado.replace("[CARRERA_ACTIVA]", str(career))
        prompt_con_estado = prompt_con_estado.replace("[ETAPA_ACTUAL]", current_stage)

        print(f"[STRATEGY] Analizando con {agente_estrat.name} (Contexto: {contexto})...")
        strategy_raw = agente_estrat.run(message, session, system_override=prompt_con_estado)
        strategy_data = parse_strategic_json(strategy_raw)
        
        # Extraer data estratégica
        detected_intent = strategy_data.get("intent", intent)
        suggested_stage = strategy_data.get("stage", current_stage)
        response_type = strategy_data.get("response_type", "template")
        
        # Sticky Context: Solo cambiar contexto si el agente detecta uno nuevo MUY claro (lia vs egel)
        # y no tenemos una carrera académica fija
        if strategy_data.get("detected_context") and not career:
            session["contexto"] = strategy_data.get("detected_context")
            contexto = session["contexto"]

        # 3. SALES FLOW ENGINE (Guiar conversación)
        # El engine decide la respuesta basada en el flow predefinido
        flow_response, next_stage = advance_flow(session, detected_intent, contexto, career=session.get("career"))
        
        print(f"[FLOW] {current_stage} -> {next_stage}")
        print(f"[INTENT] {detected_intent}")
        print(f"[PRODUCT] {contexto}")

        # 4. GENERACIÓN DE RESPUESTA
        clean_msg = ""
        
        # PRIORIDAD ABSOLUTA AL TEMPLATE SI NO SE PIDE AI EXPLÍCITAMENTE
        if response_type == "template" and flow_response:
            print("[RESPONSE] TEMPLATE")
            clean_msg = flow_response
        else:
            # Solo usamos AI para preguntas abiertas, objeciones complejas o si no hay template
            print("[RESPONSE] AI (Fast Mode)")
            clean_msg = agente_estrat.run(message, session, system_override=FAST_PROMPT)

        # Fallback de seguridad
        if not clean_msg:
            clean_msg = flow_response if flow_response else get_template_response("fallback", contexto, career=session.get("career"))

        # ===== LEAD SCORING & CRM =====
        score = session.get("lead_score", 0)
        if "pricing" in detected_intent: score += 2
        if "urgency" in detected_intent: score += 3
        if next_stage in ["presentation", "closing"]: score += 4
        
        session["lead_score"] = score
        session["lead_nivel"] = "HOT" if score >= 8 else "WARM" if score >= 4 else "COLD"

        # Actualizar Agente según etapa del flow (simplificado)
        if next_stage in ["pain_point", "presentation"]:
            session["agente_actual"] = "agente_2"
        elif next_stage in ["closing", "done"]:
            session["agente_actual"] = "agente_3"

        update_lead(session_id, {
            "etapa": next_stage,
            "lead_score": score,
            "lead_nivel": session["lead_nivel"],
            "ultimo_contexto": contexto,
            "carrera": session.get("career")
        })

        # ===== HISTORIAL =====
        session["history"].append({"role": "user", "content": message})
        session["history"].append({"role": "assistant", "content": clean_msg})
        if len(session["history"]) > 6:
            session["history"] = session["history"][-6:]

    except Exception as e:
        print(f"[PIPELINE ERROR] {e}")
        return {
            "response": "Perdón 😅 tuve un pequeño problema procesando tu mensaje.",
            "agent": "fallback",
            "lead_score": 0
        }

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