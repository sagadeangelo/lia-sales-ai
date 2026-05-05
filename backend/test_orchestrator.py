import sys
import os

# Agregar el directorio backend al path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from orchestrator import run_pipeline, parse_response

def test_parsing():
    print("--- Test Parsing ---")
    response = """
---MENSAJE---
Hola, bienvenido a LIA. ¿Qué carrera estudias?

---JSON---
{
    "agente": "agente_1",
    "siguiente_agente": "agente_2",
    "carrera": "Derecho"
}
"""
    msg, data = parse_response(response)
    print(f"Mensaje: {msg}")
    print(f"JSON: {data}")
    assert msg == "Hola, bienvenido a LIA. ¿Qué carrera estudias?"
    assert data["carrera"] == "Derecho"
    print("Parsing OK!")

def test_pipeline_logic():
    print("\n--- Test Pipeline Logic (Mocking Agent) ---")
    
    # Mocking agente_1.run directly in the module
    import orchestrator
    original_run = orchestrator.agente_1.run
    
    orchestrator.agente_1.run = lambda m, s: """---MENSAJE---
Genial, te pasaré con calificación.
---JSON---
{"siguiente_agente": "agente_2", "nombre": "Juan"}
"""

    session = {"agente_actual": "agente_1"}
    msg = run_pipeline(session, "Hola, soy Juan")
    
    print(f"Resultado: {msg}")
    print(f"Session: {session}")
    
    assert session["agente_actual"] == "agente_2"
    assert session["nombre"] == "Juan"
    assert msg == "Genial, te pasaré con calificación."
    
    # Restaurar
    orchestrator.agente_1.run = original_run
    print("Pipeline Logic OK!")

if __name__ == "__main__":
    try:
        test_parsing()
        test_pipeline_logic()
        print("\n¡Todas las pruebas locales pasaron!")
    except Exception as e:
        print(f"\nError en las pruebas: {e}")
