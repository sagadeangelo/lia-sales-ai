import random
import time

from crm.manager import update_lead

from response_engine import (
    detect_career,
    CAREER_DATA
)

from sales.intent_detector import detect_intent
from sales.sales_templates import RESPONSES
from sales.sales_flows import advance_flow
from sales.ai_humanizer import humanize


# ==========================================
# FALLBACKS
# ==========================================

FALLBACKS = [

    "¡Claro! 😊 Cuéntame un poquito más.",

    "Sí 👌 puedo ayudarte con eso.",

    "🔥 Va. Te explico rapidísimo.",

    "👀 Claro. Mucha gente pregunta eso antes de comenzar.",
]


# ==========================================
# DIRECT INTENTS
# ==========================================

DIRECT_INTENTS = [

    "pricing_question",

    "difference_question",

    "buy_intent",

    "fear_question",

    "access_question",

    "duration_question"
]

# ==========================================
# HELPERS
# ==========================================

def inject_dynamic_data(text, career):

    if not text:
        return text

    if not career:
        # If no career, we don't replace or we use general placeholders
        return text

    career_info = CAREER_DATA.get(
        career,
        {}
    )

    precio = career_info.get(
        "precio",
        499
    )

    text = text.replace(
        "[CARRERA]",
        career
    )

    text = text.replace(
        "[PRECIO]",
        str(precio)
    )

    return text


# ==========================================
# HYBRID PIPELINE
# ==========================================

def run_pipeline(session_id, session, message):

    start_total = time.time()

    try:

        # ==================================
        # SESSION SAFETY
        # ==================================

        session.setdefault("history", [])
        session.setdefault("sales_stage", "idle")
        session.setdefault("conversation_stage", "idle")
        session.setdefault("contexto", "general")
        session.setdefault("exam_context", {
            "career": None,
            "exam_type": "EGEL",
            "subcategory": None
        })

        # ==================================
        # DETECT CAREER
        # ==================================

        new_career = detect_career(message)

        if new_career:
            session["exam_context"]["career"] = new_career
            session["contexto"] = "egel"
            
            # If we were waiting for career, or just started, send the confirmation intro
            if session.get("conversation_stage") in ["awaiting_career", "idle"]:
                
                template = RESPONSES.get("career_confirmed_intro")
                career = new_career # ensure it's used for injection
                
                final_response = inject_dynamic_data(template, career)
                final_response = humanize(final_response)
                
                session["conversation_stage"] = "career_confirmed"
                session["sales_stage"] = "interest" # jump to interest in the flow
                
                print(f"[RESPONSE] CAREER CONFIRMED: {new_career}")
                
                # Save to history
                session["history"].append({"role": "user", "content": message})
                session["history"].append({"role": "assistant", "content": final_response})
                
                return final_response

            session["conversation_stage"] = "career_detected"

            print(f"[CAREER DETECTED] {new_career}")

        # Current career from context
        exam_ctx = session.get("exam_context", {})
        career = exam_ctx.get("career")

        # ==================================
        # CONTEXT
        # ==================================

        contexto = session.get(
            "contexto",
            "general"
        )

        # ==================================
        # DETECT INTENT
        # ==================================

        intent = detect_intent(message)
        session["intent"] = intent

        print(f"[INTENT] {intent}")
        print(f"[CTX] {contexto}")
        print(f"[STAGE] {session.get('conversation_stage')}")

        # ==================================
        # SAVE LAST MESSAGE
        # ==================================

        session["last_user_message"] = message

        # ==================================
        # PRIORITY 0:
        # CAREER ENFORCEMENT
        # ==================================

        egel_intents = [
            "pricing_question",
            "access_question",
            "buy_intent",
            "difference_question",
            "egel_interest",
            "duration_question"
        ]

        if not career and intent in egel_intents:
            
            # Check if we already asked
            if session.get("conversation_stage") != "awaiting_career":
                
                template = RESPONSES.get("ask_career_natural")
                session["conversation_stage"] = "awaiting_career"
                
                final_response = humanize(template)
                
                print("[RESPONSE] FORCED CAREER DETECTION")
                
                # Save to history
                session["history"].append({"role": "user", "content": message})
                session["history"].append({"role": "assistant", "content": final_response})
                
                return final_response

        # ==================================
        # PRIORITY 1:
        # DIRECT RESPONSES
        # ==================================

        if intent in DIRECT_INTENTS:

            template = RESPONSES.get(intent)

            if template:

                response = inject_dynamic_data(
                    template,
                    career
                )

                final_response = humanize(
                    response
                )

                print("[RESPONSE] TEMPLATE DIRECT")

                # SAVE HISTORY

                session["history"].append({
                    "role": "user",
                    "content": message
                })

                session["history"].append({
                    "role": "assistant",
                    "content": final_response
                })

                if len(session["history"]) > 8:

                    session["history"] = session["history"][-8:]

                # CRM

                update_lead(session_id, {
                    "career": career,
                    "exam_context": session.get("exam_context"),
                    "contexto": contexto,
                    "intent": intent,
                    "stage": session.get("sales_stage"),
                    "conversation_stage": session.get("conversation_stage")
                })

                elapsed_total = (
                    time.time() - start_total
                )

                print(
                    f"⚡ PIPELINE: {elapsed_total:.2f}s"
                )

                return final_response

        # ==================================
        # PRIORITY 2:
        # FLOW SYSTEM
        # ==================================

        flow_response, next_stage = advance_flow(

            session=session,

            intent=intent,

            product_context=contexto,

            career=career
        )

        print("[RESPONSE] FLOW")

        base_response = flow_response

        # ==================================
        # FALLBACK
        # ==================================

        if not base_response:

            base_response = random.choice(
                FALLBACKS
            )

        # ==================================
        # HUMANIZER
        # ==================================

        final_response = humanize(
            base_response
        )

        # ==================================
        # SAVE HISTORY
        # ==================================

        session["history"].append({
            "role": "user",
            "content": message
        })

        session["history"].append({
            "role": "assistant",
            "content": final_response
        })

        if len(session["history"]) > 8:

            session["history"] = session["history"][-8:]

        # ==================================
        # CRM
        # ==================================

        update_lead(session_id, {
            "career": career,
            "exam_context": session.get("exam_context"),
            "contexto": contexto,
            "intent": intent,
            "stage": session.get("sales_stage"),
            "conversation_stage": session.get("conversation_stage")
        })

        elapsed_total = (
            time.time() - start_total
        )

        print(
            f"⚡ PIPELINE: {elapsed_total:.2f}s"
        )

        return final_response

    except Exception as e:

        print(f"[PIPELINE ERROR] {e}")

        return (
            "😅 Perdón, tuve un pequeño problema "
            "procesando tu mensaje."
        )