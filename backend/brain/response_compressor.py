# ==========================================
# RESPONSE COMPRESSOR
# ==========================================

import re


def compress_response(text):

    # ==========================================
    # ELIMINAR EXCESO DE ESPACIOS
    # ==========================================

    text = re.sub(r'\s+', ' ', text).strip()

    # ==========================================
    # REEMPLAZAR BULLETS EXCESIVOS
    # ==========================================

    text = text.replace("•", "·")

    # ==========================================
    # ELIMINAR FRASES REPETITIVAS
    # ==========================================

    repetitive = [
        "Eso ayuda muchísimo",
        "Mucha gente",
        "Nuestro sistema",
        "Muchos alumnos",
        "La mayoría empieza",
        "Perfecto",
        "Excelente",
    ]

    for r in repetitive:
        text = text.replace(r, "")

    # ==========================================
    # LIMITAR TAMAÑO
    # ==========================================

    if len(text) > 320:
        text = text[:320] + "..."

    # ==========================================
    # LIMPIEZA FINAL
    # ==========================================

    text = text.replace("  ", " ")
    text = text.replace(" .", ".")
    text = text.strip()

    return text