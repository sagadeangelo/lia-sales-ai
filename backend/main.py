from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

from orchestrator import run_pipeline

from crm.manager import add_historial, update_lead
from crm.storage import load_data

from memory.session_memory import (
    get_session,
    update_session,
    add_message
)

from brain.intent_score import calculate_intent
from brain.hot_detector import is_hot_lead

import traceback
import uuid

from brain.context_manager import context_manager
from brain.sales_stage import detect_sales_stage
from brain.response_router import enrich_response
from brain.response_compressor import compress_response
from sales.ai_humanizer import humanize as humanize_response

from quiz.routes.quiz_routes import router as quiz_router


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="LIA Sales AI",
    version="3.0.0",
    description="Sistema Inteligente Conversacional"
)

print("\n" + "="*50)
print("🚀 LIA SALES AI INICIANDO")
print("✅ Sistema comercial activo")
print("="*50 + "\n")

# =========================================================
# QUIZ ROUTES
# =========================================================

app.include_router(quiz_router)

# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lia.lasagadeangelo.com.mx",
        "https://agents.lasagadeangelo.com.mx",
        "https://lia-landing.pages.dev",

        "http://localhost:3000",
        "http://127.0.0.1:3000",

        "http://localhost:5500",
        "http://127.0.0.1:5500",

        "http://localhost:8000",
        "http://127.0.0.1:8000",

        "*"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# CONFIG
# =========================================================

MAX_HISTORY = 8
sessions = {}

# =========================================================
# MODELS
# =========================================================

class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str
    contexto: str | None = None

# =========================================================
# UTILS
# =========================================================

def clean_response(text: str):

    if not text:
        return ""

    text = text.replace("\\n\\n", " ")
    text = text.replace("\\n", " ")

    return " ".join(text.split())

def get_or_create_session(session_id=None):

    if not session_id:
        session_id = str(uuid.uuid4())

    if session_id not in sessions:

        sessions[session_id] = {
            "agente_actual": "agente_1",
            "history": [],
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "contexto": None,
            "lead_score": 0,
            "lead_nivel": "COLD",
            "etapa": "captura"
        }

    return session_id, sessions[session_id]

# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "system": "LIA SALES AI",
        "version": "3.0.0"
    }

# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "sessions": len(sessions),
        "timestamp": datetime.now().isoformat()
    }

# =========================================================
# CHAT
# =========================================================

@app.post("/chat")
async def chat(req: ChatRequest):

    try:

        # =====================================================
        # SESSION
        # =====================================================

        session_id, session = get_or_create_session(req.session_id)

        session["last_activity"] = datetime.now().isoformat()

        user_message = req.message.strip()

        # ==========================================
        # CONTEXTO MEMORIA
        # ==========================================
        context = context_manager.get(session_id)
        context_manager.increment_messages(session_id)

        # =====================================================
        # CONTEXTO
        # =====================================================

        if req.contexto:
            session["contexto"] = req.contexto

        # =====================================================
        # MEMORY SYSTEM
        # =====================================================

        memory = get_session(session_id)

        add_message(
            session_id,
            "user",
            user_message
        )

        # =====================================================
        # INTENT SCORE
        # =====================================================

        new_score = calculate_intent(user_message)

        total_score = memory["intent_score"] + new_score

        hot = is_hot_lead(total_score)

        # =====================================================
        # UPDATE MEMORY
        # =====================================================

        update_session(session_id, {
            "intent_score": total_score,
            "hot_lead": hot
        })

        # =====================================================
        # UPDATE SESSION
        # =====================================================

        session["lead_score"] = total_score

        if hot:
            session["lead_nivel"] = "HOT"
            session["etapa"] = "cierre"

        elif total_score >= 30:
            session["lead_nivel"] = "WARM"
            session["etapa"] = "evaluacion"

        else:
            session["lead_nivel"] = "COLD"
            session["etapa"] = "captura"

        # =====================================================
        # HISTORY USER
        # =====================================================

        session["history"].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })

        # =====================================================
        # PIPELINE
        # =====================================================

        raw_response = run_pipeline(
            session_id,
            session,
            user_message
        )

        # ==========================================
        # ACTUALIZAR CONTEXTO
        # ==========================================
        intent = session.get("intent", "general")
        career = session.get("career", "Derecho")

        # Detectar etapa de venta
        stage = detect_sales_stage(user_message, context)

        context_manager.update(session_id, {
            "intent": intent,
            "career": career,
            "last_question": user_message,
            "conversation_stage": stage
        })

        print(f"[STAGE] {stage}")

        # =====================================================
        # RESPONSE CLEAN
        # =====================================================

        if isinstance(raw_response, dict):
            raw_text = raw_response.get("response", "")
        else:
            raw_text = raw_response

        response = clean_response(raw_text)

        # ==========================================
        # ENRIQUECER RESPUESTA (ROUTER)
        # ==========================================
        response = enrich_response(
            response=response,
            stage=stage,
            context=context
        )

        # ==========================================
        # HUMANIZAR (FINAL)
        # ==========================================
        response = humanize_response(response)

        # ==========================================
        # COMPRIMIR (FINAL)
        # ==========================================
        response = compress_response(response)

        print("[COMPRESSED]")
        print(f"[ROUTED_STAGE] {stage}")
        print(f"[FINAL_RESPONSE] {response}")

        # =====================================================
        # MEMORY AI
        # =====================================================

        add_message(
            session_id,
            "assistant",
            response
        )

        # =====================================================
        # HISTORY AI
        # =====================================================

        session["history"].append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

        # =====================================================
        # LIMIT HISTORY
        # =====================================================

        if len(session["history"]) > MAX_HISTORY:
            session["history"] = session["history"][-MAX_HISTORY:]

        # =====================================================
        # SAVE SESSION
        # =====================================================

        sessions[session_id] = session

        # =====================================================
        # CRM
        # =====================================================

        add_historial(
            session_id,
            user_message,
            response
        )

        update_lead(session_id, {
            "producto_actual": session.get("producto"),
            "carrera": session.get("carrera"),
            "etapa": session.get("etapa"),
            "lead_score": session.get("lead_score"),
            "lead_nivel": session.get("lead_nivel"),
            "ultimo_contexto": session.get("contexto"),
            "ultima_actividad": datetime.now().isoformat()
        })

        # ==========================================
        # GUARDAR ULTIMA RESPUESTA
        # ==========================================
        context_manager.update(session_id, {
            "last_response": response
        })

        # =====================================================
        # LOGS
        # =====================================================

        print(f"[CHAT] {session_id}")
        print(f"[MSG] {user_message}")
        print(f"[INTENT] {intent}")
        print(f"[MEMORY] {context_manager.debug(session_id)}")
        print(f"[CTX] {session.get('contexto')}")
        print(f"[AGENT] {session.get('agente_actual')}")
        print(f"[SCORE] {total_score}")
        print(f"[HOT LEAD] {hot}")
        print(f"[LEAD] {session.get('lead_nivel')}")
        print(f"[STAGE] {session.get('etapa')}")
        print("------------------------------------------------")

        # =====================================================
        # RESPONSE
        # =====================================================

        return {
            "success": True,
            "session_id": session_id,
            "response": response,
            "etapa": session.get("etapa"),
            "agente": session.get("agente_actual"),
            "lead_score": session.get("lead_score"),
            "lead_nivel": session.get("lead_nivel"),
            "hot_lead": hot,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:

        print("\n[ERROR CHAT]")
        traceback.print_exc()
        print("------------------------------------------------")

        return {
            "success": False,
            "response": "Híjole, tuve un pequeño problema procesando tu mensaje. 😅 ¿Me lo podrías repetir?",
            "error": str(e)
        }

# =========================================================
# DASHBOARD
# =========================================================

@app.get("/dashboard")
def dashboard():

    data = load_data()

    total_leads = len(data)

    activos = sum(
        1 for u in data.values()
        if u.get("estado") != "cerrado"
    )

    ventas_totales = sum(
        len(u.get("ventas", []))
        for u in data.values()
    )

    conversion = (
        ventas_totales / total_leads * 100
        if total_leads > 0 else 0
    )

    hot = sum(
        1 for u in data.values()
        if u.get("lead_nivel") == "HOT"
    )

    return {
        "status": "online",
        "total_leads": total_leads,
        "leads_activos": activos,
        "total_ventas": ventas_totales,
        "conversion": round(conversion, 2),
        "hot_leads": hot,
        "sessions_online": len(sessions)
    }

# =========================================================
# LEADS
# =========================================================

@app.get("/leads")
def leads():

    data = load_data()

    return [
        {
            "id": sid,
            "producto": u.get("producto_actual"),
            "carrera": u.get("carrera"),
            "etapa": u.get("etapa"),
            "ventas": len(u.get("ventas", [])),
            "lead_score": u.get("lead_score"),
            "lead_nivel": u.get("lead_nivel")
        }

        for sid, u in data.items()
    ]

# =========================================================
# VENTAS
# =========================================================

@app.get("/ventas")
def ventas():

    data = load_data()

    result = []

    for sid, u in data.items():

        for v in u.get("ventas", []):

            result.append({
                "session_id": sid,
                "producto": v.get("producto"),
                "precio": v.get("precio"),
                "carrera": v.get("carrera"),
                "fecha": v.get("fecha")
            })

    return result

# =========================================================
# EMBUDO
# =========================================================

@app.get("/embudo")
def embudo():

    data = load_data()

    funnel = {
        "captura": 0,
        "evaluacion": 0,
        "cierre": 0
    }

    for u in data.values():

        etapa = u.get("etapa") or "captura"

        if etapa in funnel:
            funnel[etapa] += 1

    return funnel

# =========================================================
# DASHBOARD UI
# =========================================================

@app.get("/dashboard-ui", response_class=HTMLResponse)
def dashboard_ui():

    return """
    <html>
    <head>
        <title>LIA SALES AI</title>
        <meta charset="utf-8"/>

        <style>

            body{
                background:#020617;
                color:white;
                font-family:Arial;
                padding:30px;
            }

            h1{
                color:#8b5cf6;
            }

            .card{
                background:#111827;
                border-radius:16px;
                padding:20px;
                margin-bottom:20px;
            }

            .grid{
                display:grid;
                grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
                gap:20px;
            }

            .value{
                font-size:32px;
                font-weight:bold;
                margin-top:10px;
            }

        </style>
    </head>

    <body>

        <h1>🚀 LIA SALES AI</h1>

        <div class="grid">

            <div class="card">
                <h3>Sessions</h3>
                <div id="sessions" class="value">0</div>
            </div>

            <div class="card">
                <h3>Leads</h3>
                <div id="leads" class="value">0</div>
            </div>

            <div class="card">
                <h3>Ventas</h3>
                <div id="ventas" class="value">0</div>
            </div>

            <div class="card">
                <h3>Conversión</h3>
                <div id="conversion" class="value">0%</div>
            </div>

        </div>

        <script>

        async function load(){

            const d = await fetch('/dashboard')
                .then(r=>r.json());

            sessions.innerText = d.sessions_online;
            leads.innerText = d.total_leads;
            ventas.innerText = d.total_ventas;
            conversion.innerText = d.conversion + "%";
        }

        load();

        setInterval(load,3000);

        </script>

    </body>
    </html>
    """