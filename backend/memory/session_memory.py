from datetime import datetime

MEMORY = {}


def get_session(user_id: str):

    if user_id not in MEMORY:

        MEMORY[user_id] = {
            "created_at": str(datetime.now()),
            "career": None,
            "exam_date": None,
            "intent_score": 0,
            "asked_price": False,
            "requested_link": False,
            "hot_lead": False,
            "conversation_stage": "idle",
            "messages": []
        }

    return MEMORY[user_id]


def update_session(user_id: str, data: dict):

    session = get_session(user_id)

    for key, value in data.items():
        session[key] = value

    return session


def add_message(user_id: str, role: str, text: str):

    session = get_session(user_id)

    session["messages"].append({
        "role": role,
        "text": text
    })

    # Limitar memoria
    if len(session["messages"]) > 20:
        session["messages"] = session["messages"][-20:]