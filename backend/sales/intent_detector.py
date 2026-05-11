from response_engine import CAREERS

def detect_intent(message):

    if not message:
        return "general"

    msg = message.lower().strip()

    # =========================================
    # SHORT CAREER RESPONSE
    # =========================================

    if msg in CAREERS:
        return "egel_interest"

    # =========================================
    # PRICING
    # =========================================

    pricing_words = [

        "precio",
        "cuanto cuesta",
        "cuánto cuesta",

        "cuanto vale",
        "cuánto vale",

        "costo",
        "vale",

        "$",

        "mensualidad",

        "pago"
    ]

    for w in pricing_words:

        if w in msg:
            return "pricing_question"

    # =========================================
    # ACCESS TIME / DURATION
    # =========================================

    duration_questions = [

        "cuanto tiempo",
        "cuánto tiempo",

        "por cuanto tiempo",
        "por cuánto tiempo",

        "es de por vida",
        "tiene vencimiento",

        "caduca",

        "hasta cuando",
        "hasta cuándo",

        "cuanto dura",
        "cuánto dura",

        "el acceso dura",

        "para siempre",

        "cuanto tiempo puedo usar",
        "cuánto tiempo puedo usar"
    ]

    for q in duration_questions:

        if q in msg:
            return "duration_question"
    # =========================================
    # DIFFERENCE
    # =========================================

    if (
        "diferencia" in msg
        and (
            "simulador" in msg
            or "guia" in msg
            or "guía" in msg
        )
    ):

        return "difference_question"

    # =========================================
    # ACCESS / INCLUDES
    # =========================================

    access_questions = [

        "que incluye",
        "qué incluye",

        "que trae",
        "qué trae",

        "que contiene",
        "qué contiene",

        "como funciona",
        "cómo funciona",

        "que es el acceso",
        "qué es el acceso",

        "a que te refieres con el acceso",
        "a qué te refieres con el acceso",

        "como se usa",
        "cómo se usa",

        "que obtengo",
        "qué obtengo",

        "que me incluye",
        "qué me incluye",

        "que trae el acceso",
        "qué trae el acceso"
    ]

    for q in access_questions:

        if q in msg:
            return "access_question"

    # =========================================
    # BUY INTENT
    # =========================================

    buy_words = [

        "quiero comprar",
        "quiero adquirir",

        "me interesa",

        "quiero entrar",

        "quiero comenzar",

        "quiero acceso",

        "como compro",
        "cómo compro",

        "como pago",
        "cómo pago",

        "dame acceso",

        "pasame el acceso",
        "pásame el acceso",

        "quiero la guia",
        "quiero la guía",

        "quiero el simulador"
    ]

    for w in buy_words:

        if w in msg:
            return "buy_intent"

    # =========================================
    # FEAR / ANXIETY
    # =========================================

    fear_words = [

        "miedo",
        "nervio",
        "nervios",

        "estres",
        "estrés",

        "ansiedad",

        "preocupado",
        "preocupada",

        "siento que no puedo",

        "no estoy listo",
        "no estoy lista",

        "me da miedo reprobar"
    ]

    for w in fear_words:

        if w in msg:
            return "fear_question"

    # =========================================
    # EGEL INTEREST
    # =========================================

    egel_words = [

        "egel",

        "guia",
        "guía",

        "simulador",

        "ceneval",

        "examen",

        "derecho",
        "psicologia",
        "psicología",
        "enfermeria",
        "enfermería",
        "administracion",
        "administración",
        "contaduria",
        "contaduría",
        "ingenieria",
        "ingeniería",
        "medicina",

        "quiero informes",
        "quiero información",
        "informes de las guías",
        "quiero estudiar",
        "quiero prepararme",
        "ayuda para el examen",
        "promociones"
    ]

    for w in egel_words:

        if w in msg:
            return "egel_interest"

    # =========================================
    # LIA
    # =========================================

    lia_words = [

        "libro",
        "novela",
        "historia",

        "ia",
        "inteligencia artificial",

        "personajes",
        "mundo",
        "saga",

        "escritor",
        "escribir"
    ]

    for w in lia_words:

        if w in msg:
            return "lia_interest"

    # =========================================
    # GENERAL
    # =========================================

    return "general"