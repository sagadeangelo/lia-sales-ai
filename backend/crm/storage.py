import json
import os

# Ruta persistente local
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

def load_data():
    """Carga el JSON de base de datos local."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.strip():
                return {}
            return json.loads(content)
    except (json.JSONDecodeError, Exception) as e:
        print(f"[CRM STORAGE] Error cargando datos: {e}")
        return {}

def save_data(data):
    """Guarda el diccionario completo en el JSON."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[CRM STORAGE] Error guardando datos: {e}")

def get_user(session_id):
    """Obtiene un usuario específico por session_id."""
    data = load_data()
    return data.get(session_id)

def save_user(session_id, user_data):
    """Actualiza o crea un usuario en el almacenamiento."""
    data = load_data()
    data[session_id] = user_data
    save_data(data)
