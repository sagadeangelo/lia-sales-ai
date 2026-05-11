# ============================================
# LIA TRAIN - RESPONSE ENGINE
# ============================================

# ============================================
# CARRERAS DETECTABLES
# ============================================

CAREERS = [

    # DERECHO
    "derecho",

    # PSICOLOGIA
    "psicologia",
    "psicología",

    # ADMIN
    "administracion",
    "administración",

    # CONTA
    "contabilidad",
    "contaduria",
    "contaduría",

    # SISTEMAS / TI
    "sistemas",
    "ti",
    "informatica",
    "informática",
    "software",
    "programacion",
    "programación",

    # INDUSTRIAL
    "industrial",
    "ingenieria industrial",
    "ingeniería industrial",

    # INGENIERIA GENERAL
    "ingenieria",
    "ingeniería",

    # ENFERMERIA
    "enfermeria",
    "enfermería",

    # MEDICINA
    "medicina",
    "medico",
    "médico",

    # ARQUITECTURA
    "arquitectura",

    # EDUCACION
    "educacion",
    "educación",

    # PEDAGOGIA
    "pedagogia",
    "pedagogía",

    # COMERCIO
    "comercio"
]

# ============================================
# CARRERAS DISPONIBLES
# ============================================

CAREER_DATA = {

    # ============================================
    # ACTIVAS
    # ============================================

    "Derecho": {
        "emoji": "⚖️",
        "precio": 499,
        "status": "active"
    },

    "Enfermería": {
        "emoji": "🩺",
        "precio": 499,
        "status": "active"
    },

    "Psicología": {
        "emoji": "🧠",
        "precio": 499,
        "status": "active"
    },

    "Administración": {
        "emoji": "📊",
        "precio": 499,
        "status": "active"
    },

    "Contaduría": {
        "emoji": "💼",
        "precio": 499,
        "status": "active"
    },

    "Ingeniería": {
        "emoji": "⚙️",
        "precio": 499,
        "status": "active"
    },

    "Sistemas / TI": {
        "emoji": "💻",
        "precio": 499,
        "status": "active"
    },

    "Ing. Industrial": {
        "emoji": "🏭",
        "precio": 499,
        "status": "active"
    },

    # ============================================
    # PRÓXIMAMENTE
    # ============================================

    "Medicina": {
        "emoji": "🩻",
        "precio": 499,
        "status": "coming_soon"
    },

    "Arquitectura": {
        "emoji": "🏛️",
        "precio": 499,
        "status": "coming_soon"
    },

    "Educación": {
        "emoji": "📚",
        "precio": 499,
        "status": "coming_soon"
    },

    "Pedagogía": {
        "emoji": "🧒",
        "precio": 499,
        "status": "coming_soon"
    },

    "Comercio": {
        "emoji": "🌎",
        "precio": 499,
        "status": "coming_soon"
    }
}


# ============================================
# NORMALIZAR NOMBRES
# ============================================

def normalize_career(career):

    if not career:
        return None

    career = career.lower().strip()

    replacements = {

        # DERECHO
        "derecho": "Derecho",

        # PSICOLOGIA
        "psicologia": "Psicología",
        "psicología": "Psicología",

        # ADMIN
        "administracion": "Administración",
        "administración": "Administración",

        # CONTA
        "contabilidad": "Contaduría",
        "contaduria": "Contaduría",
        "contaduría": "Contaduría",

        # SISTEMAS
        "sistemas": "Sistemas / TI",
        "ti": "Sistemas / TI",
        "informatica": "Sistemas / TI",
        "informática": "Sistemas / TI",
        "software": "Sistemas / TI",
        "programacion": "Sistemas / TI",
        "programación": "Sistemas / TI",

        # INDUSTRIAL
        "industrial": "Ing. Industrial",
        "ingenieria industrial": "Ing. Industrial",
        "ingeniería industrial": "Ing. Industrial",

        # INGENIERIA
        "ingenieria": "Ingeniería",
        "ingeniería": "Ingeniería",

        # ENFERMERIA
        "enfermeria": "Enfermería",
        "enfermería": "Enfermería",

        # MEDICINA
        "medicina": "Medicina",
        "medico": "Medicina",
        "médico": "Medicina",

        # ARQUITECTURA
        "arquitectura": "Arquitectura",

        # EDUCACION
        "educacion": "Educación",
        "educación": "Educación",

        # PEDAGOGIA
        "pedagogia": "Pedagogía",
        "pedagogía": "Pedagogía",

        # COMERCIO
        "comercio": "Comercio"
    }

    return replacements.get(
        career,
        career.capitalize()
    )


# ============================================
# DETECTAR CARRERA
# ============================================

def detect_career(message):

    if not message:
        return None

    msg = message.lower()

    # Detectar carreras más específicas primero
    sorted_careers = sorted(
        CAREERS,
        key=len,
        reverse=True
    )

    for career in sorted_careers:

        if career in msg:

            detected = normalize_career(career)

            print(f"[CAREER DETECTED] {detected}")

            return detected

    return None


# ============================================
# OBTENER INFO CARRERA
# ============================================

def get_career_data(career_name):

    if not career_name:
        return None

    return CAREER_DATA.get(
        career_name
    )


# ============================================
# FALLBACK INTELIGENTE
# ============================================

def get_intelligent_fallback():
    return (
        "No te preocupes 😊\n\n"
        "Puedes decirme tu carrera, examen o área de interés y te ayudo "
        "a encontrar la guía correcta."
    )


# ============================================
# DISPONIBILIDAD
# ============================================

def is_career_available(career_name):

    data = get_career_data(career_name)

    return data.get("status") == "active"


# ============================================
# PRECIO
# ============================================

def get_career_price(career_name):

    data = get_career_data(career_name)

    return data.get("precio", 499)


# ============================================
# EMOJI
# ============================================

def get_career_emoji(career_name):

    data = get_career_data(career_name)

    return data.get("emoji", "🎓")