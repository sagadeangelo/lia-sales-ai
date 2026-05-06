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

EGEL_RESPONSES = {
    "intro": """¡Claro! 🎓 Nuestro simulador EGEL [CARRERA] incluye:
• preguntas tipo CENEVAL
• temporizador real
• análisis inteligente
• práctica por áreas

¿Ya sabes cuándo presentarás el examen?""",

    "precio": """💳 Tenemos acceso completo al simulador, entrenamiento y materiales de apoyo para [CARRERA].

¿Quieres que te explique qué incluye exactamente?""",

    "urgencia": """🔥 Si ya presentarás pronto el examen de [CARRERA], te recomiendo empezar cuanto antes para medir tu nivel real."""
}

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

def format_template(text, career=None):
    if not career:
        career = "Derecho" # Default si no se detecta nada pero es EGEL
    return text.replace("[CARRERA]", career)

def get_template_response(intent, context="general", career=None):
    response = ""
    if "egel" in intent or context == "egel":
        if "pricing" in intent or "precio" in intent:
            response = EGEL_RESPONSES["precio"]
        elif "urgency" in intent:
            response = EGEL_RESPONSES["urgencia"]
        else:
            response = EGEL_RESPONSES["intro"]
        return format_template(response, career)
        
    if "lia" in intent or context == "lia_staylo":
        if "pricing" in intent or "precio" in intent:
            return LIA_RESPONSES["features"]
        return LIA_RESPONSES["intro"]
        
    if intent == "greeting":
        return GENERAL_RESPONSES["greeting"]
        
    if intent == "pricing":
        return GENERAL_RESPONSES["pricing_generic"]
        
    return GENERAL_RESPONSES["fallback"]
