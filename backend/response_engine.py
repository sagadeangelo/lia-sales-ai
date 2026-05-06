import re

EGEL_RESPONSES = {
    "intro": """¡Claro! ⚖️ Nuestro simulador EGEL Derecho incluye:
• preguntas tipo CENEVAL
• temporizador real
• análisis inteligente
• práctica por áreas

¿Ya sabes cuándo presentarás el examen?""",

    "precio": """💳 Tenemos acceso completo al simulador, entrenamiento y materiales de apoyo.

¿Quieres que te explique qué incluye exactamente?""",

    "urgencia": """🔥 Si ya presentarás pronto el examen, te recomiendo empezar cuanto antes para medir tu nivel real."""
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

def detect_intent(message):
    msg = message.lower()
    
    # Intenciones de EGEL
    if any(x in msg for x in ["egel", "simulador", "examen", "derecho", "ceneval"]):
        if any(x in msg for x in ["precio", "costo", "cuanto", "pago"]):
            return "egel_pricing"
        return "egel_interest"
    
    # Intenciones de LIA
    if any(x in msg for x in ["lia", "staylo", "libros", "escritor", "historias", "personajes"]):
        if any(x in msg for x in ["precio", "costo", "cuanto", "pago"]):
            return "lia_pricing"
        return "lia_interest"
    
    # Precios genéricos
    if any(x in msg for x in ["precio", "costo", "cuanto cuesta", "pago"]):
        return "pricing"
        
    # Urgencia
    if any(x in msg for x in ["pronto", "urgente", "ya", "mañana", "esta semana"]):
        return "urgency"
        
    # Objeciones
    if any(x in msg for x in ["caro", "duda", "desconfianza", "seguro", "funciona"]):
        return "objection"
        
    # Saludos
    if any(x in msg for x in ["hola", "buenos dias", "que tal", "quien eres"]):
        return "greeting"

    return "general"

def get_template_response(intent, context="general"):
    if "egel" in intent or context == "egel":
        if "pricing" in intent or "precio" in intent:
            return EGEL_RESPONSES["precio"]
        if "urgency" in intent:
            return EGEL_RESPONSES["urgencia"]
        return EGEL_RESPONSES["intro"]
        
    if "lia" in intent or context == "lia_staylo":
        if "pricing" in intent or "precio" in intent:
            return LIA_RESPONSES["features"] # O un template de precio LIA
        return LIA_RESPONSES["intro"]
        
    if intent == "greeting":
        return GENERAL_RESPONSES["greeting"]
        
    if intent == "pricing":
        return GENERAL_RESPONSES["pricing_generic"]
        
    return GENERAL_RESPONSES["fallback"]
