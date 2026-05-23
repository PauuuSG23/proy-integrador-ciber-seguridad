# chat_gemini_qa_promptInjection

Repositorio de ejemplo para evaluar y probar vulnerabilidades de "prompt injection"
en un flujo cliente-servidor que usa un modelo de lenguaje (Gemini API).

## Resumen
Este proyecto contiene una pequeña aplicación Flask (`app.py`) que sirve una
interfaz web (`templates/index.html` + `static/script.js`) y una suite de pruebas
en `qa-tests/` para analizar cómo se comporta el sistema frente a payloads maliciosos.

## Estructura principal
- `app.py` - Servidor Flask (endpoint `/chat`).
- `templates/` - Plantillas HTML (interfaz del chat).
- `static/` - JS/CSS/imagenes usados por la UI.
- `qa-tests/` - Pruebas automatizadas y payloads para QA.

## Requisitos (Windows)
- Python 3.10+ (o la versión compatible que uses).
- `requirements.txt` incluye dependencias principales.

## Instalación y ejecución (recomendado)
1. Crear entorno virtual:

   py -m venv .venv

2. Activar el entorno (PowerShell):

   .\.venv\Scripts\Activate.ps1

3. Actualizar pip e instalar dependencias:

   python -m pip install --upgrade pip
   pip install -r requirements.txt

4. Ejecutar la aplicación:

   python app.py

La aplicación expone un endpoint `/chat` que el frontend usa vía `fetch`.

## Pruebas QA (prompt injection)
1. Ir al directorio de pruebas:

   cd qa-tests

2. Ejecutar las pruebas:

   python test_prompt_injection.py

3. Los reportes se generan en `qa-tests/reports/` en formatos JSON/Excel/HTML.

## Notas sobre el flujo
- Usuario → `index.html` → `static/script.js` → `/chat` (Flask) → Gemini API → respuesta.

## Desarrollo
- Para agregar payloads de prueba edita `qa-tests/payloads.json`.
- `qa-tests/metrics.py` contiene utilidades para evaluar resultados y generar reportes.

## Contacto
Para dudas o mejoras abre un issue o contacta al autor.

---
Actualizado: contenido reorganizado para claridad y pasos reproducibles.