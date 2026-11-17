from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List
import datetime
import random

app = FastAPI(title="API de Re-Inscripción al Tec")

# ==========================================
# 1. MODELOS DE DATOS (INTERFAZ DE ENTRADA)
# ==========================================
class GrupoSeleccionado(BaseModel):
    id_materia: str = Field(..., description="Clave de la materia")
    id_grupo: str = Field(..., description="Clave del grupo")

class SolicitudReinscripcion(BaseModel):
    numero_control: str = Field(..., pattern=r"^\d{8}$", description="Número de control de 8 dígitos numéricos")
    contrasena: str = Field(..., description="Contraseña del alumno para validar identidad")
    periodo: str = Field(..., description="Periodo escolar")
    # Se quitó el min_items para manejar el error manualmente con un mensaje más limpio
    grupos_seleccionados: List[GrupoSeleccionado] = Field(..., description="Lista de materias a inscribir")

# ==========================================
# 2. ENDPOINT DE LA API (LÓGICA DEL SISTEMA)
# ==========================================
@app.post("/api/reinscripcion")
async def procesar_reinscripcion(solicitud: SolicitudReinscripcion):
    """
    Recibe la Interfaz de Entrada, valida credenciales y procesa la inscripción.
    """
    # 1. Validación manual para evitar listas vacías con un mensaje amigable (HTTP 400)
    if len(solicitud.grupos_seleccionados) == 0:
        raise HTTPException(status_code=400, detail="Debes seleccionar al menos una materia para re-inscribirte.")
    
    # 2. Validación de credenciales
    usuario_valido = "23281280"
    contrasena_valida = "CarvajalAguilar*93"
    
    if solicitud.numero_control != usuario_valido or solicitud.contrasena != contrasena_valida:
        raise HTTPException(status_code=401, detail="Número de control o contraseña incorrectos.")
    
    # 3. Respuesta de éxito (Interfaz de Salida - HTTP 200)
    folio = f"FOL-{random.randint(100000, 999999)}"
    
    return {
        "status": "success",
        "mensaje": "Re-inscripción completada correctamente.",
        "datos": {
            "numero_control": solicitud.numero_control,
            "folio_inscripcion": folio,
            "fecha_hora": datetime.datetime.now().isoformat(),
            "materias_inscritas": len(solicitud.grupos_seleccionados)
        }
    }

# ==========================================
# 3. PANTALLA DE ENTRADA (FRONTEND HTML/JS)
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def mostrar_pantalla():
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Sistema de Re-Inscripción</title>
        <style>
            body { font-family: system-ui, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; background-color: #f4f4f9; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            input[type="text"], input[type="password"], button { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }
            button { background-color: #0056b3; color: white; border: none; cursor: pointer; font-weight: bold; }
            button:hover { background-color: #004494; }
            pre { background: #2d2d2d; color: #00ffcc; padding: 15px; border-radius: 5px; overflow-x: auto; font-size: 13px; }
            .error { color: #ff6b6b; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Pantalla de Re-Inscripción</h2>
            <form id="formInscripcion">
                <label>Número de Control (8 dígitos):</label>
                <input type="text" id="numControl" value="23281280" required pattern="\\d{8}" title="Debe contener exactamente 8 números">
                
                <label>Contraseña:</label>
                <input type="password" id="contrasena" placeholder="Ingresa tu contraseña" required>
                
                <label>Periodo:</label>
                <input type="text" id="periodo" value="2026-2" readonly>
                
                <h3>Selecciona tus grupos:</h3>
                <div>
                    <input type="checkbox" id="mat1" value="M-105|G-401"> <label>Graficación (G-401)</label><br>
                    <input type="checkbox" id="mat2" value="M-108|G-402"> <label>Lenguajes y Autómatas (G-402)</label><br>
                    <input type="checkbox" id="mat3" value="M-110|G-403"> <label>Ingeniería de Software (G-403)</label>
                </div>
                
                <button type="submit">Autenticar e Inscribir</button>
            </form>
        </div>

        <div class="card" style="margin-top: 20px;">
            <h3>Interfaz de Salida (Respuesta del Servidor):</h3>
            <pre id="resultado">Esperando petición...</pre>
        </div>

        <script>
            document.getElementById('formInscripcion').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const gruposSeleccionados = [];
                const checkboxes = ['mat1', 'mat2', 'mat3'];
                
                checkboxes.forEach(id => {
                    const cb = document.getElementById(id);
                    if (cb.checked) {
                        const [id_materia, id_grupo] = cb.value.split('|');
                        gruposSeleccionados.push({ id_materia, id_grupo });
                    }
                });

                // 1. Validación en el frontend antes de enviar a la API
                if (gruposSeleccionados.length === 0) {
                    document.getElementById('resultado').className = "error";
                    document.getElementById('resultado').innerText = JSON.stringify({
                        "detail": "Por favor selecciona al menos una materia."
                    }, null, 2);
                    return; // Detiene la ejecución para no hacer la petición al servidor
                }

                const payload = {
                    numero_control: document.getElementById('numControl').value,
                    contrasena: document.getElementById('contrasena').value,
                    periodo: document.getElementById('periodo').value,
                    grupos_seleccionados: gruposSeleccionados
                };

                document.getElementById('resultado').innerText = "Procesando...";
                document.getElementById('resultado').className = "";

                try {
                    const response = await fetch('/api/reinscripcion', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    
                    const data = await response.json();
                    
                    if (!response.ok) {
                        document.getElementById('resultado').className = "error";
                    }
                    document.getElementById('resultado').innerText = JSON.stringify(data, null, 2);
                } catch (error) {
                    document.getElementById('resultado').className = "error";
                    document.getElementById('resultado').innerText = "Error de conexión con el servidor.";
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)