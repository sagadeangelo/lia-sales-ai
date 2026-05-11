# ==========================================
# LIA CONTEXT MANAGER
# ==========================================

class ContextManager:

    def __init__(self):
        self.context = {}

    # ==========================================
    # CREAR SESION
    # ==========================================

    def init_session(self, session_id):

        if session_id not in self.context:

            self.context[session_id] = {
                "last_topic": None,
                "last_product": None,
                "last_question": None,
                "conversation_stage": "inicio",
                "last_response": None,
                "messages_count": 0,
                "career": None,
                "intent": None
            }

    # ==========================================
    # OBTENER CONTEXTO
    # ==========================================

    def get(self, session_id):

        self.init_session(session_id)

        return self.context[session_id]

    # ==========================================
    # ACTUALIZAR
    # ==========================================

    def update(self, session_id, data):

        self.init_session(session_id)

        self.context[session_id].update(data)

    # ==========================================
    # AUMENTAR MENSAJES
    # ==========================================

    def increment_messages(self, session_id):

        self.init_session(session_id)

        self.context[session_id]["messages_count"] += 1

    # ==========================================
    # DEBUG
    # ==========================================

    def debug(self, session_id):

        self.init_session(session_id)

        return self.context[session_id]


# ==========================================
# INSTANCIA GLOBAL
# ==========================================

context_manager = ContextManager()