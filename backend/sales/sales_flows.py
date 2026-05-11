# sales_flows.py

from response_engine import CAREER_DATA


# ==========================================
# EGEL FLOW
# ==========================================

EGEL_FLOW = {

    "idle": {
        "next": "interest"
    },

    "interest": {
        "response": """¡Claro! [EMOJI]

Nuestro simulador EGEL [CARRERA] incluye:

• preguntas tipo CENEVAL
• temporizador real
• análisis inteligente
• práctica por áreas

¿Ya sabes cuándo presentarás el examen?""",

        "next": "exam_date"
    },

    "exam_date": {
        "response": """Perfecto [EMOJI]

Todavía tienes muy buen tiempo para prepararte para [CARRERA].

La mayoría empieza practicando para detectar primero en qué áreas anda más débil.

¿Ya has hecho algún simulador EGEL antes?""",

        "next": "experience"
    },

    "experience": {
        "response": """Excelente 🙌

Eso ayuda muchísimo para medir tu nivel actual.

Nuestro sistema te muestra:
• áreas fuertes
• áreas débiles
• progreso real
• simulaciones tipo examen

¿Hay alguna materia o área que te preocupe más?""",

        "next": "pain_point"
    },

    "pain_point": {
        "response": """Te entiendo [EMOJI]

Mucha gente llega sintiendo:
• presión por el tiempo
• nervios por el examen
• dudas sobre qué estudiar primero

Justo por eso el simulador ayuda muchísimo 👀

¿Te gustaría ver cómo funciona el entrenamiento?""",

        "next": "trust"
    },

    "trust": {
        "response": """🔥 Mucha gente usa el simulador para:

• practicar bajo tiempo real
• detectar errores
• mejorar seguridad
• acostumbrarse al formato CENEVAL

Y todo queda guardado para que puedas medir tu avance.""",

        "next": "presentation"
    },

    "presentation": {
        "response": """🚀 La guía de [CARRERA] incluye:

• simulaciones reales
• preguntas tipo CENEVAL
• análisis inteligente
• práctica por áreas
• temporizador real

Y puedes usarla desde celular o computadora.""",

        "next": "pricing"
    },

    "pricing": {
        "response": """💳 El acceso a la guía de [CARRERA] está disponible actualmente en:

$[PRECIO] MXN

Y el acceso es inmediato 👌

¿Te gustaría que te explique cómo comenzar hoy mismo?""",

        "next": "closing"
    },

    "closing": {
        "response": """⚡ Perfecto.

En cuanto realizas el acceso ya puedes comenzar a practicar inmediatamente.

Muchos empiezan practicando el mismo día para medir su nivel real 👀""",

        "next": "done"
    },

    "done": {
        "response": """😄 Aquí sigo para ayudarte.

Puedes preguntarme:
• precios
• carreras
• cómo funciona
• acceso
• simuladores
• recomendaciones""",

        "next": "done"
    }
}


# ==========================================
# LIA FLOW
# ==========================================

LIA_FLOW = {

    "idle": {
        "next": "interest"
    },

    "interest": {
        "response": """✨ LIA es una plataforma de IA enfocada en escritores y creadores.

Puedes:
• crear libros inmersivos
• desarrollar personajes
• generar historias
• construir mundos
• usar asistentes IA personalizados

¿Qué tipo de proyecto te gustaría crear?""",

        "next": "project_type"
    },

    "project_type": {
        "response": """🔥 Suena increíble.

Muchos usuarios usan LIA para:
• novelas
• sagas
• lore
• storytelling inmersivo
• universos ficticios

¿Ya tienes una historia iniciada o empezarías desde cero?""",

        "next": "experience"
    },

    "experience": {
        "response": """Perfecto ✨

La IA puede ayudarte tanto si ya tienes ideas avanzadas como si apenas estás comenzando.

La idea es que LIA funcione como un copiloto creativo.""",

        "next": "usage"
    },

    "usage": {
        "response": """🚀 LIA ayuda muchísimo a:

• desbloquear ideas
• organizar mundos
• expandir historias
• crear personajes complejos
• acelerar creatividad

¿Te gustaría conocer algunas herramientas específicas?""",

        "next": "presentation"
    },

    "presentation": {
        "response": """✨ LIA está pensada para ayudarte a construir experiencias inmersivas mucho más rápido usando IA.

Muchos creadores la usan diariamente para expandir sus proyectos.""",

        "next": "closing"
    },

    "closing": {
        "response": """⚡ Perfecto.

Puedes comenzar a usar LIA y crear tus primeros proyectos desde hoy mismo 👀""",

        "next": "done"
    },

    "done": {
        "response": """😄 Aquí sigo para ayudarte.

Puedes preguntarme:
• herramientas
• funciones
• escritura
• mundos
• personajes
• storytelling""",

        "next": "done"
    }
}


# ==========================================
# INTENT MAP
# ==========================================

INTENT_STAGE_MAP = {

    # =========================
    # EGEL
    # =========================

    "egel_interest": "interest",

    "egel_pricing": "pricing",

    "egel_buy_intent": "closing",

    "egel_fear": "trust",

    "egel_exam_date": "exam_date",

    "egel_experience": "experience",

    "egel_pain": "pain_point",

    # =========================
    # LIA
    # =========================

    "lia_interest": "interest",

    "lia_pricing": "presentation",

    "lia_buy_intent": "closing",

    # =========================
    # GENERAL
    # =========================

    "greeting": "interest"
}


# ==========================================
# HELPERS
# ==========================================

def build_dynamic_response(response, career):

    if not response:
        return "😅 Perdón, tuve un pequeño problema generando la respuesta."

    if not career:
        # We don't default anymore. If missing, we return the base response.
        return response

    career_key = career.lower()

    career_info = CAREER_DATA.get(
        career_key,
        {}
    )

    precio = career_info.get("precio", "---")
    emoji = career_info.get("emoji", "🎓")

    response = response.replace("[CARRERA]", career.title())
    response = response.replace("[PRECIO]", str(precio))
    response = response.replace("[EMOJI]", emoji)

    return response


# ==========================================
# MAIN FLOW ENGINE
# ==========================================

def advance_flow(session, intent, product_context, career=None):

    try:

        # ==================================
        # SESSION DATA
        # ==================================

        message = session.get(
            "last_user_message",
            ""
        ).lower()

        current_stage = session.get(
            "sales_stage",
            "idle"
        )

        # ==================================
        # FLOW SELECTION
        # ==================================

        if product_context == "lia_staylo":
            flow = LIA_FLOW
        else:
            flow = EGEL_FLOW

        # ==================================
        # DEFAULT NEXT STAGE
        # ==================================

        next_stage = flow.get(
            current_stage,
            {}
        ).get(
            "next",
            "interest"
        )

        # ==================================
        # INTENT OVERRIDES
        # ==================================

        if intent in INTENT_STAGE_MAP:

            next_stage = INTENT_STAGE_MAP[intent]

        # ==================================
        # MESSAGE OVERRIDES
        # ==================================

        if "precio" in message:
            next_stage = "pricing"

        elif "cuanto cuesta" in message:
            next_stage = "pricing"

        elif "costa" in message:
            next_stage = "pricing"

        elif "comprar" in message:
            next_stage = "closing"

        elif "quiero comprar" in message:
            next_stage = "closing"

        elif "me interesa" in message:
            next_stage = "presentation"

        elif "nervio" in message:
            next_stage = "trust"

        elif "miedo" in message:
            next_stage = "trust"

        elif "reprob" in message:
            next_stage = "trust"

        # ==================================
        # STAGE VALIDATION
        # ==================================

        stage_data = flow.get(next_stage)

        if not stage_data:

            print(f"[FLOW WARNING] Stage inexistente: {next_stage}")

            next_stage = "interest"

            stage_data = flow.get(next_stage)

        # ==================================
        # RESPONSE VALIDATION
        # ==================================

        response = stage_data.get("response")

        if not response:

            print(f"[FLOW WARNING] Response vacía en stage: {next_stage}")

            next_stage = "interest"

            stage_data = flow.get(next_stage)

            response = stage_data.get("response")

        # ==================================
        # FINAL SAFETY CHECK
        # ==================================

        if not response:

            return (
                "😅 Perdón, tuve un pequeño problema continuando la conversación.",
                current_stage
            )

        # ==================================
        # DYNAMIC REPLACEMENTS
        # ==================================

        if product_context != "lia_staylo":

            response = build_dynamic_response(
                response,
                career
            )

        # ==================================
        # SAVE SESSION
        # ==================================

        session["sales_stage"] = next_stage

        # ==================================
        # DEBUG LOGS
        # ==================================

        print(f"[FLOW] {current_stage} -> {next_stage}")
        print(f"[INTENT] {intent}")
        print(f"[PRODUCT] {product_context}")
        print(f"[CAREER] {career}")

        # ==================================
        # RETURN
        # ==================================

        return response, next_stage

    except Exception as e:

        print(f"[FLOW ERROR] {e}")

        return (
            "😅 Perdón, tuve un pequeño problema procesando tu mensaje.",
            "idle"
        )