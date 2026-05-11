import random


HUMAN_PREFIXES = [

    "🔥",

    "👌",

    "✨",

    "🚀",

    "👀",

    "🙌",

    "😄"
]


def humanize(text):

    if not text:
        return text

    text = text.strip()

    # evitar doble emoji
    if any(
        text.startswith(x)
        for x in HUMAN_PREFIXES
    ):
        return text

    prefix = random.choice(
        HUMAN_PREFIXES
    )

    return f"{prefix} {text}"