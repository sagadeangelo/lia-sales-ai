from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from orchestrator import run_pipeline, MODEL, BASE_URL
from crm.manager import add_historial, update_lead
from crm.storage import load_data
import traceback
import uuid
import os

# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="LIA Sales AI",
    version="2.0.0",
    description="Sistema Inteligente Conversacional"
)

print("\n" + "="*50)
print(f"LIA SALES AI INICIANDO")
print(f"MODELO ACTIVO: {MODEL}")
print(f"API URL: {BASE_URL}")
print("="*50 + "\n")

# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lia.lasagadeangelo.com.mx",
        "https://lia-landing.pages.dev",
        "http://localhost:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# CONFIG
# =========================================================

MAX_HISTORY = 6
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

def clean_response(text: str) -> str:
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
            "contexto": None
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
        "version": "2.0.0"
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

        session_id, session = get_or_create_session(req.session_id)

        session["last_activity"] = datetime.now().isoformat()

        # =====================================================
        # CONTEXTO
        # =====================================================

        if req.contexto:
            session["contexto"] = req.contexto

        # =====================================================
        # HISTORY USER
        # =====================================================

        session["history"].append({
            "role": "user",
            "content": req.message,
            "timestamp": datetime.now().isoformat()
        })

        # =====================================================
        # PIPELINE
        # =====================================================

        raw_response = run_pipeline(
            session_id,
            session,
            req.message
        )

        response = clean_response(raw_response)

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
            req.message,
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

        # =====================================================
        # LOGS
        # =====================================================

        print(f"[CHAT] {session_id}")
        print(f"[CTX] {session.get('contexto')}")
        print(f"[AGENT] {session.get('agente_actual')}")
        print(f"[LEAD] {session.get('lead_nivel')}")
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
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:

        print("\n[ERROR CHAT]")
        traceback.print_exc()
        print("------------------------------------------------")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# DASHBOARD API
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
        "calificacion": 0,
        "nurturing": 0,
        "objeciones": 0,
        "cierre": 0,
        "venta": 0,
        "postventa": 0
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