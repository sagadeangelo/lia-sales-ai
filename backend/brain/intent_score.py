BUY_WORDS = [
    "comprar",
    "precio",
    "costo",
    "link",
    "pago",
    "acceso",
    "quiero",
    "hoy",
    "inmediato",
    "deposito",
    "tarjeta",
    "transferencia",
    "guia",
    "simulador"
]


def calculate_intent(message: str):

    score = 0

    text = message.lower()

    for word in BUY_WORDS:

        if word in text:
            score += 15

    return score