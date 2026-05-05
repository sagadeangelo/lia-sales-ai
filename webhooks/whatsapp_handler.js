/**
 * webhooks/whatsapp_handler.js
 * Recibe mensajes de WhatsApp via Twilio y los enruta al agente correcto en n8n
 * 
 * Instalar: npm install express twilio axios redis
 * Correr:   node whatsapp_handler.js
 */

const express = require('express');
const { createClient } = require('redis');
const axios = require('axios');

const app = express();
app.use(express.urlencoded({ extended: false }));
app.use(express.json());

// ─── Configuración ─────────────────────────────
const CONFIG = {
  n8n_webhook: process.env.N8N_WEBHOOK_URL || 'http://localhost:5678',
  redis_url: process.env.REDIS_URL || 'redis://localhost:6379',
  twilio_token: process.env.TWILIO_AUTH_TOKEN,
  port: process.env.WEBHOOK_PORT || 4000,
};

// ─── Redis para estado de sesiones ────────────
let redis;
(async () => {
  redis = createClient({ url: CONFIG.redis_url });
  redis.on('error', (err) => console.error('Redis error:', err));
  await redis.connect();
  console.log('✅ Redis conectado');
})();

// ─── Helper: obtener o crear sesión del lead ──
async function getSession(phone) {
  const key = `session:${phone}`;
  const data = await redis.get(key);
  if (data) return JSON.parse(data);
  
  // Sesión nueva
  return {
    phone,
    canal: 'whatsapp',
    agente_actual: 'agente_1',
    nombre: null,
    carrera: null,
    fecha_egel: null,
    clasificacion: null,
    mayor_dolor: null,
    urgencia: null,
    reprobado_antes: null,
    guia_recomendada: null,
    historial: [],
    creado_en: new Date().toISOString(),
    actualizado_en: new Date().toISOString(),
  };
}

async function saveSession(phone, session) {
  const key = `session:${phone}`;
  session.actualizado_en = new Date().toISOString();
  await redis.set(key, JSON.stringify(session), { EX: 60 * 60 * 24 * 7 }); // 7 días
}

// ─── Ruta principal: recibe mensajes de Twilio ─
app.post('/webhook/whatsapp', async (req, res) => {
  try {
    const { From, Body, MessageSid } = req.body;
    
    if (!From || !Body) {
      return res.status(400).send('Datos incompletos');
    }

    const phone = From.replace('whatsapp:', '');
    const mensaje = Body.trim();

    console.log(`📱 WhatsApp de ${phone}: "${mensaje}"`);

    // Obtener sesión actual del lead
    const session = await getSession(phone);
    
    // Agregar mensaje al historial
    session.historial.push({
      rol: 'usuario',
      mensaje,
      timestamp: new Date().toISOString(),
    });

    // Enviar al orquestador n8n con el estado completo
    const respuesta = await axios.post(
      `${CONFIG.n8n_webhook}/webhook/mensaje-entrante`,
      {
        canal: 'whatsapp',
        phone,
        mensaje,
        session,
        agente_objetivo: session.agente_actual,
      },
      { timeout: 30000 }
    );

    // n8n devuelve la respuesta del agente y el estado actualizado
    const { respuesta_agente, session_actualizada } = respuesta.data;

    // Guardar sesión actualizada
    if (session_actualizada) {
      await saveSession(phone, session_actualizada);
    }

    // Responder con TwiML (Twilio espera esto)
    const twiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Message>${respuesta_agente || ''}</Message>
</Response>`;

    res.type('text/xml').send(twiml);

  } catch (error) {
    console.error('❌ Error en webhook WhatsApp:', error.message);
    
    // Respuesta de error amigable al usuario
    const twiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Message>Tuvimos un problema técnico. Intenta de nuevo en un momento 🙏</Message>
</Response>`;
    res.type('text/xml').send(twiml);
  }
});

// ─── Ruta: recibe confirmación de aprobación (Agente 6) ──
app.post('/webhook/aprobacion', async (req, res) => {
  try {
    const { phone, accion, token } = req.body;

    // Validar token básico de seguridad
    if (token !== process.env.APPROVAL_SECRET_TOKEN) {
      return res.status(403).json({ error: 'No autorizado' });
    }

    const session = await getSession(phone);

    if (accion === 'aprobar') {
      session.agente_actual = 'agente_7';
      console.log(`✅ Cierre aprobado para ${phone}`);
    } else if (accion === 'nurturing') {
      session.agente_actual = 'agente_3';
      console.log(`🔄 Regresando a nurturing: ${phone}`);
    } else if (accion === 'rechazar') {
      session.agente_actual = 'cerrado';
      console.log(`❌ Lead rechazado: ${phone}`);
    }

    await saveSession(phone, session);

    // Disparar el siguiente agente en n8n
    await axios.post(`${CONFIG.n8n_webhook}/webhook/continuar-flujo`, {
      phone,
      accion,
      session,
    });

    res.json({ ok: true, accion, phone });

  } catch (error) {
    console.error('❌ Error en aprobación:', error.message);
    res.status(500).json({ error: error.message });
  }
});

// ─── Ruta: confirmar compra (webhook de pago) ──
app.post('/webhook/compra-confirmada', async (req, res) => {
  try {
    // MercadoPago o Stripe envían datos diferentes — normalizamos
    const email = req.body?.data?.payer?.email || req.body?.data?.object?.customer_email;
    const monto = req.body?.data?.transaction_amount || req.body?.data?.object?.amount_total / 100;
    
    if (!email) {
      return res.status(400).json({ error: 'Email no encontrado en webhook de pago' });
    }

    console.log(`💰 Compra confirmada: ${email} — $${monto} MXN`);

    // Buscar sesión por email (necesita estar guardado en sesión)
    // Activar Agente 8
    await axios.post(`${CONFIG.n8n_webhook}/webhook/activar-postventa`, {
      email,
      monto,
      timestamp: new Date().toISOString(),
    });

    res.json({ ok: true });

  } catch (error) {
    console.error('❌ Error en confirmación de compra:', error.message);
    res.status(500).json({ error: error.message });
  }
});

// ─── Health check ──────────────────────────────
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    redis: redis?.isReady ? 'connected' : 'disconnected'
  });
});

// ─── Arrancar servidor ─────────────────────────
app.listen(CONFIG.port, () => {
  console.log(`🚀 Webhook WhatsApp corriendo en puerto ${CONFIG.port}`);
  console.log(`📍 Configura en Twilio: POST http://TU-IP:${CONFIG.port}/webhook/whatsapp`);
});

module.exports = app;
