from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from orchestrator import run_pipeline
from crm.manager import add_historial, update_lead
from crm.storage import load_data

app = FastAPI()

MAX_HISTORY = 20
sessions = {}

# =========================
# MODELO REQUEST
# =========================
class ChatRequest(BaseModel):
    session_id: str
    message: str
    contexto: str = None  # 🔥 NUEVO


# =========================
# UTIL
# =========================
def clean_response(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\\n\\n", " ")
    text = text.replace("\\n", " ")
    return " ".join(text.split())


# =========================
# CHAT
# =========================
@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        session = sessions.get(req.session_id, {
            "agente_actual": "agente_1",
            "history": []
        })

        # 🔥 CONTEXTO
        if req.contexto:
            session["contexto"] = req.contexto

        raw_response = run_pipeline(req.session_id, session, req.message)
        response = clean_response(raw_response)

        session["history"].append({"role": "user", "content": req.message})
        session["history"].append({"role": "assistant", "content": response})

        if len(session["history"]) > MAX_HISTORY:
            session["history"] = session["history"][-MAX_HISTORY:]

        sessions[req.session_id] = session

        # CRM
        add_historial(req.session_id, req.message, response)

        update_lead(req.session_id, {
            "producto_actual": session.get("producto"),
            "carrera": session.get("carrera"),
            "etapa": session.get("etapa")
        })

        return {
            "response": response,
            "etapa": session.get("etapa"),
            "agente": session.get("agente_actual")
        }

    except Exception as e:
        print("[ERROR]:", e)
        raise HTTPException(status_code=500, detail="Error interno")


# =========================
# DASHBOARD API
# =========================
@app.get("/dashboard")
def dashboard():
    data = load_data()

    total_leads = len(data)
    activos = sum(1 for u in data.values() if u.get("estado") != "cerrado")

    ventas_totales = sum(len(u.get("ventas", [])) for u in data.values())

    conversion = (ventas_totales / total_leads * 100) if total_leads > 0 else 0

    return {
        "total_leads": total_leads,
        "leads_activos": activos,
        "total_ventas": ventas_totales,
        "conversion": round(conversion, 2)
    }


@app.get("/leads")
def leads():
    data = load_data()

    return [
        {
            "id": sid,
            "producto": u.get("producto_actual"),
            "carrera": u.get("carrera"),
            "etapa": u.get("etapa"),
            "ventas": len(u.get("ventas", []))
        }
        for sid, u in data.items()
    ]


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


# =========================
# DASHBOARD UI PRO
# =========================
@app.get("/dashboard-ui", response_class=HTMLResponse)
def dashboard_ui():
    return """
<!DOCTYPE html>
<html>
<head>
<title>CRM PRO</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body { background:#0f172a; color:white; font-family:Arial; padding:20px; }
.grid { display:grid; grid-template-columns:repeat(4,1fr); gap:20px; }
.card { background:#1e293b; padding:20px; border-radius:10px; text-align:center; }
.section { margin-top:30px; }
table { width:100%; border-collapse:collapse; }
td, th { padding:10px; border-bottom:1px solid #334155; }
button { background:#22c55e; border:none; padding:10px; border-radius:8px; cursor:pointer; }
</style>
</head>

<body>

<h1>📊 CRM PRO</h1>
<button onclick="load()">Actualizar</button>

<div class="grid">
<div class="card"><h3>Leads</h3><p id="leads"></p></div>
<div class="card"><h3>Activos</h3><p id="activos"></p></div>
<div class="card"><h3>Ventas</h3><p id="ventas"></p></div>
<div class="card"><h3>Conversión</h3><p id="conv"></p></div>
</div>

<div class="section">
<h2>Embudo</h2>
<canvas id="chart1"></canvas>
</div>

<div class="section">
<h2>Productos</h2>
<canvas id="chart2"></canvas>
</div>

<div class="section">
<h2>Leads</h2>
<table><tbody id="tabla"></tbody></table>
</div>

<script>
let c1, c2;

async function load() {
    const d = await fetch('/dashboard').then(r=>r.json());
    const l = await fetch('/leads').then(r=>r.json());
    const e = await fetch('/embudo').then(r=>r.json());
    const v = await fetch('/ventas').then(r=>r.json());

    leads.innerText = d.total_leads;
    activos.innerText = d.leads_activos;
    ventas.innerText = d.total_ventas;
    conv.innerText = d.conversion + "%";

    if(c1) c1.destroy();
    c1 = new Chart(chart1, {
        type:'bar',
        data:{labels:Object.keys(e), datasets:[{data:Object.values(e)}]}
    });

    let prod={};
    v.forEach(x=>prod[x.producto]=(prod[x.producto]||0)+1);

    if(c2) c2.destroy();
    c2 = new Chart(chart2, {
        type:'pie',
        data:{labels:Object.keys(prod), datasets:[{data:Object.values(prod)}]}
    });

    tabla.innerHTML = l.map(x=>`
        <tr>
            <td>${x.id}</td>
            <td>${x.producto||'-'}</td>
            <td>${x.carrera||'-'}</td>
            <td>${x.etapa||'-'}</td>
            <td>${x.ventas}</td>
        </tr>
    `).join('');
}

setInterval(load, 5000);
load();
</script>

</body>
</html>
"""