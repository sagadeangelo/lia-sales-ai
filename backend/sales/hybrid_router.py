from sales.intent_detector import detect_intent
from sales.sales_templates import RESPONSES

def route_message(message):

    intent = detect_intent(message)

    if intent in RESPONSES:
        return RESPONSES[intent]

    return None