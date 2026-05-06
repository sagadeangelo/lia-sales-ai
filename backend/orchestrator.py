import json
import urllib.request
import os

from config.precios import PRODUCTOS
from crm.manager import update_lead, register_sale

# CONFIGURACIÓN IA (LM STUDIO / OLLAMA)
BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:1234")
MODEL = os.getenv("OLLAMA_MODEL", "google/gemma-4-e4b")
LMSTUDIO_URL = f"{BASE_URL}/v1/chat/completions"

FAST_PROMPT = """
Eres LIA, una asesora inteligente y amigable.

Responde:
- corto
- natural
- útil
- menos de 80 palabras
- tono humano mexicano ligero

NO uses respuestas largas.
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

    def run(self, message: str, session: dict):
        import time
        start = time.time()

        if is_fast_message(message):
            messages = [
                {"role": "system", "content": FAST_PROMPT},
                {"role": "user", "content": message}
            ]
        else:
            messages = [{"role": "system", "content": self.prompt}]
            # SOLO últimos 4 mensajes del historial para performance
            history = session.get("history", [])[-4:]
            messages.extend(history)
            messages.append({"role": "user", "content": message})

        payload = {
            "model": MODEL,
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": 120
        }

        try:
            req = urllib.request.Request(
                LMSTUDIO_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )

            # Gemma optimizada: 45s timeout
            with urllib.request.urlopen(req, timeout=45) as response:
                result = json.loads(response.read().decode("utf-8"))

                if "choices" not in result:
                    print("[ERROR LM] respuesta inválida:", result)
                    return "Perdón 😅 tuve un pequeño retraso procesando tu mensaje. ¿Me lo repites rapidísimo?"

                content = result["choices"][0]["message"]["content"]
                print(f"⚡ Tiempo IA: {time.time() - start:.2f}s")
                return content

        except Exception as e:
            print(f"[ERROR AGENTE {self.name}]:", e)
            return "Perdón 😅 tuve un pequeño retraso procesando tu mensaje. ¿Me lo repites rapidísimo?"


# =========================
# PARSER
# =========================

def parse_response(response: str):
    # Si es el mensaje de fallback, no intentar parsear JSON
    if "retraso procesando tu mensaje" in response:
        return response, {}
        
    try:
        if "---MENSAJE---" in response and "---JSON---" in response:

            parts = response.split("---JSON---")

            mensaje = parts[0].replace("---MENSAJE---", "").strip()
            json_str = parts[1].strip()

            try:
                json_data = json.loads(json_str)
            except:
                json_data = {}

            return mensaje, json_data

        return response.strip(), {}

    except:
        return response.strip(), {}


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
# PIPELINE
# =========================

def run_pipeline(session_id: str, session: dict, message: str):

    session.setdefault("history", [])
    contexto = session.get("contexto", "general")
    
    print(f"\n[PIPELINE] Contexto Activo: {contexto}")

    # 🔥 PRIORIDAD ABSOLUTA DEL CONTEXTO
    if contexto == "egel":
        if not session.get("producto") or "LIA" in str(session.get("producto")):
            session["producto"] = "EGEL_DERECHO" # Default
    elif contexto == "lia_staylo":
        session["producto"] = "LIA_STAYLO"

    # ===== DETECTAR CARRERA (Solo si es EGEL) =====
    if contexto == "egel":
        carrera = detectar_carrera(message)
        if carrera:
            session["carrera"] = carrera
            session["producto"] = f"EGEL_{carrera.upper()}"

    # ===== SALTO CAPTURA =====
    if session.get("carrera") and session.get("agente_actual") == "agente_1":
        session["agente_actual"] = "agente_2"

    agente_actual = session.get("agente_actual", "agente_1")
    print(f">>> AGENTE: {agente_actual}")

    agents_map = {
        "agente_1": agente_1,
        "agente_2": agente_2,
        "agente_3": agente_3,
        "agente_4": agente_4,
        "agente_5": agente_5,
        "agente_6": agente_6,
        "agente_7": agente_7,
        "agente_8": agente_8
    }

    agente = agents_map.get(agente_actual, agente_1)

    try:
        raw_response = agente.run(message, session)
        clean_msg, json_data = parse_response(raw_response)

        # Si hubo error de fallback, no procesar más lógica de sesión
        if "retraso procesando tu mensaje" in clean_msg:
            return clean_msg

        # ===== INTENCIÓN =====
        intencion = detectar_intencion(message)

        # ===== LEAD SCORING =====
        score = 0
        if intencion == "compra":
            score += 5
        if intencion == "precio":
            score += 3
        if session.get("urgencia") == "alta":
            score += 3
        if len(session.get("history", [])) > 4:
            score += 2

        session["lead_score"] = score

        if score >= 7:
            session["lead_nivel"] = "HOT"
        elif score >= 4:
            session["lead_nivel"] = "WARM"
        else:
            session["lead_nivel"] = "COLD"

        # ===== PRODUCTOS =====
        producto_key = session.get("producto")

        if producto_key in PRODUCTOS:
            producto = PRODUCTOS[producto_key]

            clean_msg = clean_msg.replace("[PRODUCTO]", producto["nombre"])
            clean_msg = clean_msg.replace("[precio]", str(producto["precio"]))
            clean_msg = clean_msg.replace("[descripcion]", producto["descripcion"])

            session["precio"] = producto["precio"]

        # ===== CRM LIMPIO =====
        allowed_keys = ["nombre", "carrera", "producto", "precio", "etapa", "mayor_dolor", "urgencia", "lead_score", "lead_nivel"]

        clean_data = {k: v for k, v in json_data.items() if k in allowed_keys}
        
        # Guardar score en CRM
        clean_data["lead_score"] = session.get("lead_score")
        clean_data["lead_nivel"] = session.get("lead_nivel")

        if clean_data:
            update_lead(session_id, clean_data)

        # ===== SESSION UPDATE =====
        for k, v in json_data.items():
            if k not in ["agente", "siguiente_agente"]:
                session[k] = v

        # ===== CONTROL FLUJO =====
        siguiente = json_data.get("siguiente_agente")

        if intencion == "precio":
            siguiente = "agente_4"

        if intencion == "compra" or session.get("lead_nivel") == "HOT":
            siguiente = "agente_7"

        if siguiente:
            session["agente_actual"] = siguiente

        # ===== ETAPA =====
        etapa_map = {
            "agente_1": "captura",
            "agente_2": "calificacion",
            "agente_3": "nurturing",
            "agente_4": "objeciones",
            "agente_5": "cierre",
            "agente_6": "revision",
            "agente_7": "venta",
            "agente_8": "postventa"
        }

        session["etapa"] = etapa_map.get(session["agente_actual"], "captura")

        # ===== REGISTRAR VENTA =====
        if session.get("agente_actual") == "agente_7" and not session.get("venta_registrada"):

            producto = session.get("producto")
            precio = session.get("precio")

            if producto and precio:
                register_sale(
                    session_id=session_id,
                    producto=producto,
                    precio=precio,
                    carrera=session.get("carrera")
                )

                session["venta_registrada"] = True
                print("💰 VENTA REGISTRADA")

        # ===== HISTORIAL =====
        session["history"].append({"role": "user", "content": message})
        session["history"].append({"role": "assistant", "content": clean_msg})

        if len(session["history"]) > 6:
            session["history"] = session["history"][-6:]

        print(f"📊 Etapa: {session['etapa']}")
        print(f"🎯 Producto: {session.get('producto')}")
        print(f"🔥 Lead Score: {session.get('lead_score')}")
        print(f"🎯 Nivel: {session.get('lead_nivel')}")
        print(f"➡️ Siguiente: {session.get('agente_actual')}")

        return clean_msg

    except Exception as e:
        print("[ERROR CRÍTICO]:", e)
        return "Perdón 😅 tuve un pequeño retraso procesando tu mensaje. ¿Me lo repites rapidísimo?"


# =========================
# AGENTES
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "agentes", "prompts"))

agente_1 = LocalAgent("agente_1", os.path.join(PROMPTS_DIR, "agente_1_captura.md"))
agente_2 = LocalAgent("agente_2", os.path.join(PROMPTS_DIR, "agente_2_calificacion.md"))
agente_3 = LocalAgent("agente_3", os.path.join(PROMPTS_DIR, "agente_3_nurturing.md"))
agente_4 = LocalAgent("agente_4", os.path.join(PROMPTS_DIR, "agente_4_objeciones.md"))
agente_5 = LocalAgent("agente_5", os.path.join(PROMPTS_DIR, "agente_5_propuesta.md"))
agente_6 = LocalAgent("agente_6", os.path.join(PROMPTS_DIR, "agente_6_revision_humana.md"))
agente_7 = LocalAgent("agente_7", os.path.join(PROMPTS_DIR, "agente_7_cierre.md"))
agente_8 = LocalAgent("agente_8", os.path.join(PROMPTS_DIR, "agente_8_postventa.md"))