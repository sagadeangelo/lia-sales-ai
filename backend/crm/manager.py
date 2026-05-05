from datetime import datetime
from .storage import get_user, save_user
from .models import create_usuario_crm, create_venta

def get_or_create_user(session_id):
    """Busca un usuario o lo inicializa si es nuevo."""
    user = get_user(session_id)
    if not user:
        user = create_usuario_crm(session_id)
        save_user(session_id, user)
    return user

def update_lead(session_id, data_dict):
    """Actualiza campos del lead dinámicamente."""
    user = get_or_create_user(session_id)
    
    # Campos directos
    for key in ["nombre", "carrera", "etapa", "estado", "producto_actual"]:
        if key in data_dict and data_dict[key]:
            user[key] = data_dict[key]
            
    # Manejo de productos de interés (sin duplicar)
    if "producto" in data_dict:
        prod = data_dict["producto"]
        if prod not in user["productos_interes"]:
            user["productos_interes"].append(prod)
        user["producto_actual"] = prod

    user["ultima_interaccion"] = datetime.now().isoformat()
    save_user(session_id, user)

def set_producto(session_id, producto):
    """Atajo para cambiar el producto de interés."""
    update_lead(session_id, {"producto": producto})

def set_etapa(session_id, etapa):
    """Atajo para cambiar la etapa del funnel."""
    update_lead(session_id, {"etapa": etapa})

def add_historial(session_id, user_msg, bot_msg):
    """Registra la interacción en el historial (Límite 20)."""
    user = get_or_create_user(session_id)
    entry = {
        "fecha": datetime.now().isoformat(),
        "user": user_msg,
        "bot": bot_msg
    }
    user["historial"].append(entry)
    
    # Limitar historial a 20 para no inflar el JSON
    if len(user["historial"]) > 20:
        user["historial"] = user["historial"][-20:]
        
    save_user(session_id, user)

def register_sale(session_id, producto, precio, carrera=None):
    """Registra una venta y cierra el lead como exitoso."""
    user = get_or_create_user(session_id)
    venta = create_venta(producto, precio, carrera)
    user["ventas"].append(venta)
    user["estado"] = "cerrado" # Lead convertido
    save_user(session_id, user)

def get_user_summary(session_id):
    """Retorna un resumen rápido del estado del usuario."""
    user = get_user(session_id)
    if not user:
        return None
    return {
        "nombre": user.get("nombre", "Sin nombre"),
        "etapa": user.get("etapa", "captura"),
        "interes": user.get("productos_interes", []),
        "ventas_realizadas": len(user.get("ventas", []))
    }
