# ==========================================
# RESPONSE ROUTER
# ==========================================

def enrich_response(response, stage, context):

    # ==========================================
    # CIERRE
    # ==========================================

    if stage == "cierre":

        if "link" not in response.lower():

            response += "\n\n🔥 ¿Te gustaría que te pase el enlace para comenzar hoy mismo?"

    # ==========================================
    # OBJECION
    # ==========================================

    elif stage == "objecion":

        response = "👌 Muy buena pregunta\n\n" + response

    # ==========================================
    # INTERES
    # ==========================================

    elif stage == "interes":

        if context["messages_count"] > 3:

            response += "\n\n👀 Muchos alumnos empiezan practicando primero para detectar sus áreas más débiles."

    # ==========================================
    # INICIO
    # ==========================================

    elif stage == "inicio":

        if context["messages_count"] <= 1:

            response = "👋 " + response

    return response