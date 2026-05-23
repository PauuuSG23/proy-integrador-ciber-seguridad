import os # Para acceder a variables de entorno (como la API key)
from flask import Flask, request, jsonify, render_template # Flask: framework web; request: para leer datos de la petición; jsonify: para responder JSON; render_template: para HTML
from flask_cors import CORS # CORS: para permitir que el frontend (ej. en localhost:5173) hable con este backend (localhost:5000) sin bloqueos del navegador
from dotenv import load_dotenv # Para cargar variables de entorno desde un archivo .env (recomendado para no “quemar” la API key en el código)
import google.generativeai as gen # SDK de Gemini: para interactuar con los modelos de lenguaje de Google

# -----------------------------
# 1) Cargar variables de entorno
# -----------------------------
# Lee el archivo .env (si existe) y “carga” sus variables al entorno del proceso.
# Ejemplo de .env:
#   GOOGLE_API_KEY=tu_api_key_aqui
load_dotenv() # Carga variables de entorno desde .env 

# Tomamos la API Key desde variables de entorno para NO “quemarla” en el código.
API_KEY = os.getenv("GOOGLE_API_KEY")

# Validación: si no existe la variable, detenemos el programa con un error claro.
if not API_KEY:
    raise RuntimeError("Falta GOOGLE_API_KEY en entorno o .env")

# -----------------------------
# 2) Configurar el SDK de Gemini
# -----------------------------
# Se configura el cliente con tu API key.
gen.configure(api_key=API_KEY) # Configura el SDK de Gemini con tu API key para autenticación.
# Ahora el SDK sabe quién eres y puede hacer llamadas a la API de Gemini usando esa clave.
# gen. es el módulo del SDK, y configure() es la función que le dice tu API key para que pueda autenticar tus solicitudes.
# Sin esto, no podrías usar los modelos de Gemini.

# Se instancia el modelo que vas a usar.
# "gemini-2.5-flash" suele ser rápido y barato para chat general.
model = gen.GenerativeModel("gemini-2.5-flash")

# -----------------------------
# 3) Crear la app Flask
# -----------------------------
# static_folder: carpeta para archivos estáticos (CSS, JS, imágenes)
# template_folder: carpeta para templates HTML (Jinja2)
# jinja2 es el motor de plantillas que usa Flask para renderizar HTML dinámico.
app = Flask(__name__, static_folder="static", template_folder="templates")

# Habilita CORS para que tu frontend (por ejemplo en localhost:5173)
# pueda hacer fetch a tu backend (localhost:5000) sin bloqueo del navegador.
CORS(app)

# -----------------------------
# 4) Rutas / Endpoints
# -----------------------------

@app.route("/")  # Página principal
def home():
    # Renderiza templates/index.html
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
# Endpoint de chat: recibe un JSON con:
# - message: el texto del usuario (obligatorio)
# - history: lista opcional con turnos previos para contexto
def chat():
    # request.get_json(silent=True): intenta leer JSON; si falla, no lanza excepción.
    # or {}: si viene None, lo cambiamos por un diccionario vacío.
    data = request.get_json(silent=True) or {}

    # message: tomamos el campo, y le quitamos espacios al inicio/fin.
    user_msg = data.get("message", "").strip() # por defecto es cadena vacía si no viene el campo

    # history: lista con objetos tipo {"role":"user|assistant","content":"..."}
    history = data.get("history", []) # nos sirve para enviar contexto al modelo, pero no es obligatorio. Por defecto es lista vacía.

    # Si el usuario no manda mensaje, devolvemos error 400 (bad request)
    if not user_msg:
        return jsonify({"error": "Mensaje vacío"}), 400

    # --------------------------------------------
    # 5) Construir un prompt (transcript) sencillo
    # --------------------------------------------
    # Aquí “aplanas” el historial en texto con etiquetas Usuario/Asistente,
    # para que el modelo entienda el contexto.
    transcript = ""

    # history[-10:]: tomas solo los últimos 10 turnos para no enviar demasiado texto.
    for h in history[-10:]: #-10 equivale a enviar solo los últimos 10 turnos de la conversación para no saturar el prompt. ejemplo: si history tiene 20 turnos, solo se tomarán los turnos del 11 al 20 (los más recientes).  
        role = h.get("role", "user")      # por defecto user
        msg = h.get("content", "")        # por defecto vacío

        # Convertimos role a etiquetas humanas en español:
        # - role == "user" => "Usuario"
        # - cualquier otro => "Asistente"
        transcript += f"{'Usuario' if role=='user' else 'Asistente'}: {msg}\n"

    # Añadimos el mensaje actual del usuario y dejamos “Asistente:” listo
    # para que el modelo continúe respondiendo.
    transcript += f"Usuario: {user_msg}\nAsistente:"

    # --------------------------------------------
    # 6) Llamar al modelo y devolver respuesta JSON
    # --------------------------------------------
    try:
        # generate_content envía el prompt y recibe una respuesta del modelo.
        resp = model.generate_content(transcript)

        # resp.text trae el texto principal. Si viniera vacío, ponemos fallback.
        text = resp.text or "(sin respuesta)"

        # Respuesta al frontend con formato JSON
        return jsonify({"reply": text})

    except Exception as e:
        # Si algo falla (API key mala, límites, red, etc.) devolvemos error 500.
        return jsonify({"error": str(e)}), 500

# -----------------------------
# 7) Punto de entrada (ejecución)
# -----------------------------
if __name__ == "__main__":
    # Ejecuta en modo desarrollo:
    # - host 127.0.0.1 => solo accesible localmente
    # - port 5000 => puerto típico de Flask
    # - debug True => recarga automática y trazas de error (NO usar en producción)
    app.run(host="0.0.0.0", port=5000, debug=True)