EGEL_FLOW = {
    "idle": {
        "next": "interest"
    },
    "interest": {
        "response": """¡Claro! ⚖️ Nuestro simulador EGEL Derecho incluye:
• preguntas tipo CENEVAL
• temporizador real
• análisis inteligente
• práctica por áreas

¿Ya sabes cuándo presentarás el examen?""",
        "next": "exam_date"
    },
    "exam_date": {
        "response": """Perfecto ⚖️ Es muy buen tiempo para prepararte bien.

La mayoría empieza practicando para detectar en qué áreas anda más débil.

¿Ya has hecho algún simulador EGEL antes?""",
        "next": "experience"
    },
    "experience": {
        "response": """Excelente 🙌 Eso ayuda muchísimo para medir tu nivel actual.

Nuestro sistema te muestra:
• áreas fuertes
• áreas débiles
• progreso real
• simulaciones tipo examen

¿Te preocupa más alguna materia específica?""",
        "next": "pain_point"
    },
    "pain_point": {
        "response": """Te entiendo ⚖️ Mucha gente batalla justo con esa parte al inicio.

La ventaja del simulador es que puedes practicar por áreas y repetir ejercicios hasta sentir más seguridad.

¿Te gustaría ver cómo funciona el entrenamiento?""",
        "next": "presentation"
    },
    "presentation": {
        "response": """🔥 El sistema está pensado para que practiques como si ya estuvieras presentando el EGEL real.

Muchos alumnos lo usan para:
• medir nivel
• practicar bajo tiempo
• mejorar seguridad
• reducir nervios

¿Quieres que te explique qué incluye el acceso completo?""",
        "next": "closing"
    },
    "closing": {
        "response": """🚀 Perfecto. El acceso incluye simuladores, entrenamiento y herramientas de práctica diseñadas para ayudarte a llegar mucho más preparado al examen.

¿Te gustaría conocer el proceso para comenzar?""",
        "next": "done"
    }
}

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
        "response": """🔥 Suena increíble. LIA está diseñada justamente para acelerar procesos creativos sin perder tu estilo.

Muchos usuarios la usan para:
• novelas
• sagas
• universos ficticios
• storytelling inmersivo

¿Ya tienes una historia iniciada o empezarías desde cero?""",
        "next": "experience"
    },
    "experience": {
        "response": """Perfecto ✨ La IA puede ayudarte tanto si ya tienes ideas avanzadas como si apenas estás comenzando.

La idea es que LIA funcione como un copiloto creativo.

¿Te gustaría usarla más para escribir, organizar ideas o crear mundos?""",
        "next": "usage"
    },
    "usage": {
        "response": """🚀 Esa es justamente una de las partes más fuertes de LIA.

El sistema ayuda a:
• acelerar creatividad
• desbloquear ideas
• organizar lore
• expandir historias
• desarrollar personajes complejos

¿Quieres que te explique algunas herramientas específicas?""",
        "next": "presentation"
    },
    "presentation": {
        "response": """✨ LIA permite una inmersión total en tu obra. ¿Te gustaría ver cómo puedes empezar tu primer proyecto hoy mismo?""",
        "next": "closing"
    }
}

def advance_flow(session, intent, product_context, career=None):
    """
    Avanza el flujo comercial basado en el producto y el estado actual.
    """
    flow = EGEL_FLOW if product_context == "egel" else LIA_FLOW
    
    current_stage = session.get("sales_stage", "idle")
    
    # Si el usuario muestra interés directo o el intent coincide con el inicio
    if current_stage == "idle" and ("interest" in intent or "greeting" in intent):
        next_stage = "interest"
    else:
        # Avanzar al siguiente nodo del flow
        next_stage = flow.get(current_stage, {}).get("next", "interest")
    
    # Si el flow terminó o no hay más pasos, nos quedamos en el último o volvemos a interés
    if next_stage == "done":
        return None, "done"

    response = flow.get(next_stage, {}).get("response")
    
    # Reemplazo dinámico de carrera si existe
    if response and "[CARRERA]" in response:
        career_name = career if career else "Derecho"
        response = response.replace("[CARRERA]", career_name)
    
    # Actualizar sesión
    session["sales_stage"] = next_stage
    
    print(f"[FLOW] {current_stage} -> {next_stage}")
    
    return response, next_stage
