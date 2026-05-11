# ==========================================
# SALES STAGE DETECTOR
# ==========================================

def detect_sales_stage(message, context):

    text = message.lower()

    # ==========================================
    # CIERRE
    # ==========================================

    close_words = [
        "comprar",
        "link",
        "pago",
        "precio",
        "quiero",
        "me interesa",
        "donde pago",
        "como pago"
    ]

    if any(word in text for word in close_words):
        return "cierre"

    # ==========================================
    # OBJECIONES
    # ==========================================

    objection_words = [
        "diferencia",
        "vale la pena",
        "sirve",
        "funciona",
        "que incluye",
        "solo",
        "tambien",
        "ambos"
    ]

    if any(word in text for word in objection_words):
        return "objecion"

    # ==========================================
    # INTERES
    # ==========================================

    interest_words = [
        "simulador",
        "guia",
        "examen",
        "ceneval",
        "egel"
    ]

    if any(word in text for word in interest_words):
        return "interes"

    # ==========================================
    # INICIO
    # ==========================================

    if context["messages_count"] <= 2:
        return "inicio"

    # ==========================================
    # DEFAULT
    # ==========================================

    return "exploracion"