from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
historial_conversacion = []

@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():

    # =====================================================
    # COMPROBAR QUE LLEGÓ JSON
    # =====================================================

    try:
        data = request.get_json(silent=True)
    except Exception as e:
        print("ERROR AL LEER JSON:", e)
        return jsonify({
            "error": "La petición no contiene un JSON válido."
        }), 400

    if not isinstance(data, dict):
        print("ERROR: El cuerpo recibido no es un objeto JSON.")
        return jsonify({
            "error": "Formato de petición inválido."
        }), 400

    # =====================================================
    # OBTENER PREGUNTA
    # =====================================================

    pregunta = data.get("question", "")

    if not isinstance(pregunta, str):
        print("ERROR: 'question' no es texto.")
        return jsonify({
            "error": "La pregunta debe ser texto."
        }), 400

    pregunta = pregunta.strip()

    print("========================================")
    print("PREGUNTA RECIBIDA:")
    print(pregunta)
    print("LONGITUD:", len(pregunta))
    print("========================================")

    if not pregunta:
        return jsonify({
            "error": "No se recibió ninguna pregunta."
        }), 400

    # =====================================================
    # LÍMITE DE SEGURIDAD
    # =====================================================

    if len(pregunta) > 8000:
        print("ERROR: Pregunta demasiado larga.")

        return jsonify({
            "error": "La pregunta es demasiado larga."
        }), 400

    # =====================================================
    # CONSULTA A OPENAI
    # =====================================================

    try:

        respuesta = client.responses.create(
            model="gpt-5",

            instructions=(
                "Eres un asistente educativo general. "
                "Responde en español. "
                "Puedes responder preguntas de matemáticas, ciencias, historia, "
                "geografía, tecnología, cultura general y otros temas escolares. "
                "Explica las respuestas de forma clara, sencilla y breve."
            ),

            input=pregunta
        )

        texto = respuesta.output_text

        if not texto:
            print("ERROR: OpenAI devolvió una respuesta vacía.")

            return jsonify({
                "error": "OpenAI no devolvió una respuesta."
            }), 500

        print("RESPUESTA GENERADA:")
        print(texto)
        print("========================================")

        return jsonify({
            "answer": texto
        }), 200

    except Exception as e:

        print("========================================")
        print("ERROR DE OPENAI:")
        print(type(e).__name__)
        print(str(e))
        print("========================================")

        return jsonify({
            "error": "No se pudo obtener una respuesta de OpenAI."
        }), 500


# =========================================================
# INICIAR SERVIDOR
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )