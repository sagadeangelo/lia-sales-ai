import re

CAREERS = [
    "derecho",
    "psicologia",
    "psicología",
    "administracion",
    "administración",
    "contabilidad",
    "contaduria",
    "contaduría",
    "ingenieria",
    "ingeniería",
    "medicina",
    "arquitectura",
    "enfermeria",
    "enfermería",
    "educacion",
    "educación",
    "pedagogia",
    "pedagogía",
    "comercio"
]

STRONG_INTENTS = [
    "egel_interest",
    "lia_interest",
    "egel_pricing",
    "lia_pricing",
    "pricing"
]

CAREER_DATA = {
    "Derecho": {
        "features": "• preguntas tipo CENEVAL\n• temporizador real\n• análisis inteligente\n• práctica por áreas",
        "pricing": "acceso completo al simulador, entrenamiento y materiales de apoyo",
        "cta": "¿Ya sabes cuándo presentarás el examen?",
        "emoji": "⚖️"
    },
    "Enfermería": {
        "features": "• casos clínicos actualizados\n• fundamentos de enfermería\n• gestión de salud\n• práctica por áreas críticas",
        "pricing": "guías de estudio y simuladores especializados",
        "cta": "¿Ya tienes fecha para tu examen de enfermería?",
        "emoji": "🩺"
    },
    "Psicología": {
        "features": "• evaluación psicológica\n• intervención clínica\n• bases biológicas\n• simulaciones tipo EGEL",
        "pricing": "banco de preguntas y herramientas de análisis",
        "cta": "¿Te gustaría empezar a practicar con los casos clínicos?",
        "emoji": "🧠"
    },
    "Administración": {
        "features": "• mercadotecnia y finanzas\n• recursos humanos\n• administración estratégica\n• simulador tiempo real",
        "pricing": "paquete completo de entrenamiento estratégico",
        "cta": "¿Quieres ver los temas que incluye el simulador de administración?",
        "emoji": "📊"
    },
    "Contaduría": {
        "features": "• normas de información financiera\n• auditoría y fiscal\n• contabilidad de costos\n• práctica tipo CENEVAL",
        "pricing": "acceso total al sistema de práctica contable",
        "cta": "¿Te gustaría ver un demo del simulador contable?",
        "emoji": "💼"
    }
}

def build_egel_response(career_name, type="intro"):
    data = CAREER_DATA.get(career_name, CAREER_DATA["Derecho"])
    emoji = data.get("emoji", "🎓")
    
    if type == "intro":
        return f"¡Claro! {emoji} Nuestro simulador EGEL {career_name} incluye:\n{data['features']}\n\n{data['cta']}"
    
    if type == "precio":
        return f"💳 Tenemos {data['pricing']} para {career_name}. ¿Quieres que te explique qué incluye exactamente?"
    
    if type == "urgencia":
        return f"🔥 Si ya presentarás pronto el examen de {career_name}, te recomiendo empezar cuanto antes para medir tu nivel real."
    
    return f"¡Claro! 😊 Estamos listos para ayudarte con tu preparación para el EGEL {career_name}."

LIA_RESPONSES = {
    "intro": """✨ LIA es una plataforma de IA para escritores y creadores.

Puedes:
• crear libros inmersivos
• generar historias
• desarrollar personajes
• construir mundos
• usar asistentes IA personalizados

¿Qué tipo de proyecto te gustaría crear?""",

    "features": """🚀 LIA ayuda a acelerar muchísimo el proceso creativo usando IA enfocada en storytelling y contenido inmersivo."""
}

GENERAL_RESPONSES = {
    "greeting": "¡Hola! 😊 Soy LIA. ¿Te interesa el simulador EGEL o herramientas IA para escritores?",
    "pricing_generic": "¡Con gusto! 💳 Manejamos diferentes planes dependiendo de lo que necesites (EGEL o LIA). ¿De cuál te gustaría saber el costo?",
    "fallback": "¡Claro! 😊 Cuéntame más sobre lo que buscas para poder ayudarte mejor.",
    "hot_lead": "¡Excelente elección! 🚀 Veo que vas muy en serio. ¿Te gustaría ver el proceso de inscripción o prefieres resolver una duda final?"
}

def detect_career(message):
    msg = message.lower()
    for career in CAREERS:
        if career in msg:
            # Normalizar nombres para la respuesta
            if "psicologia" in career: return "Psicología"
            if "administracion" in career or "admin" in career: return "Administración"
            if "contabilidad" in career or "contaduria" in career: return "Contaduría"
            if "ingenieria" in career: return "Ingeniería"
            if "enfermeria" in career: return "Enfermería"
            if "educacion" in career or "pedagogia" in career: return "Educación"
            return career.capitalize()
    return None

def detect_intent(message):
    msg = message.lower()
    
    # 1. PRIORIDAD: Detección de Carrera (Manda a EGEL)
    career = detect_career(msg)
    if career:
        if any(x in msg for x in ["precio", "costo", "cuanto", "pago"]):
            return "egel_pricing"
        return "egel_interest"

    # 2. Palabras clave de EGEL
    if any(x in msg for x in ["egel", "simulador", "examen", "ceneval", "guia", "guía"]):
        if any(x in msg for x in ["precio", "costo", "cuanto", "pago"]):
            return "egel_pricing"
        return "egel_interest"
    
    # 3. Palabras clave de LIA
    if any(x in msg for x in ["lia", "staylo", "libros", "escritor", "escritura", "novela", "historia", "personajes", "creativo"]):
        if any(x in msg for x in ["precio", "costo", "cuanto", "pago"]):
            return "lia_pricing"
        return "lia_interest"
    
    # Precios genéricos
    if any(x in msg for x in ["precio", "costo", "cuanto cuesta", "pago"]):
        return "pricing"
        
    # Urgencia / Fechas de examen
    if any(x in msg for x in ["pronto", "urgente", "ya", "mañana", "esta semana", "meses", "año", "fecha", "presento"]):
        return "urgency"
        
    # Objeciones
    if any(x in msg for x in ["caro", "duda", "desconfianza", "seguro", "funciona"]):
        return "objection"
        
    # Saludos
    if any(x in msg for x in ["hola", "buenos dias", "que tal", "quien eres"]):
        return "greeting"

    return "general"

def get_template_response(intent, context="general", career=None):
    if not career:
        career = "Derecho" # Fallback si no hay carrera en sesión

    if "egel" in intent or context == "egel":
        if "pricing" in intent or "precio" in intent:
            return build_egel_response(career, "precio")
        elif "urgency" in intent:
            return build_egel_response(career, "urgencia")
        else:
            return build_egel_response(career, "intro")
        
    if "lia" in intent or context == "lia_staylo":
        if "pricing" in intent or "precio" in intent:
            return LIA_RESPONSES["features"]
        return LIA_RESPONSES["intro"]
        
    if intent == "greeting":
        return GENERAL_RESPONSES["greeting"]
        
    if intent == "pricing":
        return GENERAL_RESPONSES["pricing_generic"]
        
    return GENERAL_RESPONSES["fallback"]
