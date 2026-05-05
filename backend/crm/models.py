from datetime import datetime

def create_lead(session_id, nombre="", producto_actual="EGEL", carrera=None):
    """Estructura base para un lead."""
    return {
        "session_id": session_id,
        "nombre": nombre,
        "producto_actual": producto_actual,
        "carrera": carrera,
        "etapa": "captura",
        "estado": "activo",
        "fecha_creacion": datetime.now().isoformat(),
        "ultima_interaccion": datetime.now().isoformat()
    }

def create_venta(producto, precio, carrera=None):
    """Estructura base para una venta realizada."""
    return {
        "producto": producto,
        "carrera": carrera,
        "precio": precio,
        "fecha": datetime.now().isoformat()
    }

def create_usuario_crm(session_id, nombre=""):
    """Estructura maestra para el CRM local."""
    return {
        "session_id": session_id,
        "nombre": nombre,
        "carrera": None,
        "producto_actual": "EGEL",
        "etapa": "captura",
        "estado": "activo",
        "productos_interes": [],
        "historial": [],
        "ventas": [],
        "fecha_creacion": datetime.now().isoformat(),
        "ultima_interaccion": datetime.now().isoformat()
    }
