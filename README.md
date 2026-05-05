# 🤖 Sistema de Agentes de Ventas EGEL — LIA

Sistema de automatización de ventas con 8 agentes de IA para las guías EGEL de LIA. 7 agentes corren localmente con Gemma 4 en tu RTX 3050. Solo el cierre final usa Claude API.

---

## Arquitectura

```
WhatsApp → │
Email    → │ → Agente 1 (Captura) → Agente 2 (Calificación) → Agente 3 (Nurturing)
Web chat → │                                                        ↓
                                                         Agente 4 (Objeciones)
                                                                ↓
                                                    Agente 5 (Propuesta)
                                                                ↓
                                                  Agente 6 (TÚ APRUEBAS ⬅)
                                                                ↓
                                              Agente 7 (Cierre — Claude API)
                                                                ↓
                                              Agente 8 (Postventa — LOCAL)
```

---

## Requisitos previos

- Docker + Docker Compose
- NVIDIA Container Toolkit (para usar la RTX 3050)
- Ollama con Gemma 4 instalado
- Node.js 18+ (para los webhooks)
- Una cuenta de Twilio (WhatsApp)
- Una cuenta de Resend (email)
- MercadoPago o Stripe (pagos)

---

## Instalación paso a paso

### 1. Clonar y configurar variables de entorno
```bash
cp config/.env.example .env
# Abre .env y llena todos los valores
```

### 2. Verificar que Gemma 4 está instalado en Ollama
```bash
ollama list
# Debe aparecer gemma2:4b o similar
# Si no: ollama pull gemma2:4b
```

### 3. Levantar todos los servicios
```bash
docker-compose up -d
```

Esto levanta:
- **n8n** en http://localhost:5678
- **Ollama** en http://localhost:11434
- **Redis** en localhost:6379
- **Dashboard** en http://localhost:3000

### 4. Instalar dependencias de los webhooks
```bash
cd webhooks
npm install express twilio axios redis
```

### 5. Arrancar el servidor de webhooks
```bash
node whatsapp_handler.js
```

### 6. Importar el flujo en n8n
1. Ve a http://localhost:5678
2. Crea una cuenta (solo la primera vez)
3. Ve a **Workflows → Import**
4. Selecciona el archivo `flujos/pipeline_ventas.json`
5. Activa el flujo con el toggle

### 7. Configurar Twilio para WhatsApp
1. Ve a [twilio.com/console](https://console.twilio.com)
2. En **Messaging → Sandbox for WhatsApp**
3. En el campo "WHEN A MESSAGE COMES IN" pon:
   `http://TU-IP-PUBLICA:4000/webhook/whatsapp`
4. Método: POST

---

## Estructura de archivos

```
egel-ventas-agentes/
├── agentes/
│   └── prompts/
│       ├── agente_1_captura.md          ← Prompt Gemma 4 local
│       ├── agente_2_calificacion.md     ← Prompt Gemma 4 local
│       ├── agente_3_nurturing.md        ← Prompt Gemma 4 local
│       ├── agente_4_objeciones.md       ← Prompt Gemma 4 local
│       ├── agente_5_propuesta.md        ← Prompt Gemma 4 local ⚠️ actualizar catálogo
│       ├── agente_6_revision_humana.md  ← Lógica de pausa (sin LLM)
│       ├── agente_7_cierre.md           ← Prompt Claude API
│       └── agente_8_postventa.md        ← Prompt Gemma 4 local
├── flujos/
│   └── pipeline_ventas.json             ← Flujo importable en n8n
├── webhooks/
│   ├── whatsapp_handler.js              ← Recibe WhatsApp de Twilio
│   └── webchat_widget.html              ← Widget para pegar en tu sitio
├── dashboard/
│   └── index.html                       ← Panel de aprobación (Agente 6)
├── config/
│   └── .env.example                     ← Variables de entorno
├── docker-compose.yml
└── README.md
```

---

## Cómo usar el dashboard (Agente 6)

1. Abre http://localhost:3000 en tu celular o PC
2. Cuando un lead esté listo para cierre, recibirás:
   - Una notificación en Telegram
   - El lead aparece en el dashboard
3. Revisa el perfil y el historial de conversación
4. Haz clic en **✅ Aprobar y cerrar** → se activa el Agente 7
5. O en **🔄 Más nurturing** si aún no está listo

---

## Personalización importante

### Agente 5 — Actualizar tu catálogo de guías
Abre `agentes/prompts/agente_5_propuesta.md` y actualiza la sección `## Catálogo de guías` con tus productos reales: nombre, precio, URL de compra y áreas que cubre.

### Agente 3 — Contenido educativo personalizado
Agrega datos reales del EGEL relevantes para tus carreras en la sección `## Banco de contenido educativo`.

---

## Costos estimados del sistema

| Componente | Costo |
|------------|-------|
| Gemma 4 local (7 agentes) | $0 — tu GPU |
| n8n self-hosted | $0 |
| Claude API (solo cierre) | ~$0.002 USD por venta |
| Twilio WhatsApp | ~$0.005 USD por mensaje |
| Resend email | Gratis hasta 3,000 emails/mes |
| MercadoPago | 3.49% + IVA por transacción |

**Costo por venta de $299 MXN: ~$11 MXN (4%) en total de plataformas**

---

## Soporte y actualizaciones

Para reportar problemas o sugerir mejoras, contacta a Miguel en:
[wa.link/v0m2yz](https://wa.link/v0m2yz)
