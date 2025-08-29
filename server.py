import os
from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Necesario para manejar sesión en Flask

# --- Base de datos médica básica ---
symptoms_db = {
    "cáncer de mama": {
        "síntomas": [
            "bulto en el seno o axila",
            "cambios en la forma del seno",
            "secreción anormal del pezón",
            "piel enrojecida o con hoyuelos"
        ],
        "mensaje": "El cáncer de mama puede detectarse tempranamente con autoexamen y mamografía."
    },
    "cáncer de pulmón": {
        "síntomas": [
            "tos persistente o con sangre",
            "dolor en el pecho",
            "dificultad para respirar",
            "pérdida de peso inexplicada"
        ],
        "mensaje": "El cáncer de pulmón suele estar asociado al consumo de tabaco, pero también afecta a no fumadores."
    },
    "cáncer de colon": {
        "síntomas": [
            "cambios en el hábito intestinal",
            "sangrado rectal",
            "dolor abdominal persistente",
            "anemia inexplicada"
        ],
        "mensaje": "El cáncer de colon puede prevenirse con chequeos regulares y colonoscopías."
    }
}


# --- Interfaz Web ---
@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Chatbot Médico</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f6f9;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .chat-container {
                width: 450px;
                background: #fff;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            .chat-header {
                background: #4CAF50;
                color: #fff;
                padding: 15px;
                text-align: center;
                font-size: 18px;
            }
            #chat-box {
                flex: 1;
                padding: 10px;
                overflow-y: auto;
                background: #fafafa;
            }
            .user { color: #2196F3; margin: 8px 0; }
            .bot { color: #4CAF50; margin: 8px 0; }
            .input-container {
                display: flex;
                border-top: 1px solid #ddd;
            }
            input {
                flex: 1;
                padding: 10px;
                border: none;
                outline: none;
            }
            button {
                padding: 10px 15px;
                border: none;
                background: #4CAF50;
                color: #fff;
                cursor: pointer;
            }
            button:hover {
                background: #45a049;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">🤖 Chatbot Médico</div>
            <div id="chat-box"></div>
            <div class="input-container">
                <input id="user-input" type="text" placeholder="Escribe tu mensaje...">
                <button onclick="sendMessage()">Enviar</button>
            </div>
        </div>

        <script>
        async function sendMessage() {
            const input = document.getElementById("user-input");
            const message = input.value;
            if (!message) return;

            const chatBox = document.getElementById("chat-box");
            chatBox.innerHTML += `<div class='user'><b>Tú:</b> ${message}</div>`;
            input.value = "";

            try {
                const res = await fetch("/chat", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({message})
                });
                const data = await res.json();
                chatBox.innerHTML += `<div class='bot'><b>Bot:</b> ${data.response}</div>`;
                chatBox.scrollTop = chatBox.scrollHeight;
            } catch (err) {
                chatBox.innerHTML += `<div style='color:red;'><b>Error:</b> No se pudo conectar al servidor.</div>`;
            }
        }
        </script>
    </body>
    </html>
    """


# --- Lógica de conversación ---
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").lower()

    if "historia" not in session:
        session["historia"] = []

    # Guardar mensajes
    session["historia"].append({"usuario": user_message})

    response = ""

    # Buscar coincidencias con base de datos
    for cancer, data in symptoms_db.items():
        if cancer in user_message:
            response = f"El {cancer} puede presentar síntomas como: {', '.join(data['síntomas'])}. {data['mensaje']}"
            break
        for s in data["síntomas"]:
            if s in user_message:
                response = f"El síntoma que mencionas ('{s}') puede estar relacionado con el {cancer}. {data['mensaje']}"
                break

    # Si no se encontró relación
    if response == "":
        if "hola" in user_message:
            response = "¡Hola! Soy un asistente médico virtual. Puedo orientarte sobre síntomas relacionados con distintos tipos de cáncer. ¿Tienes algún síntoma específico?"
        elif "gracias" in user_message:
            response = "Con gusto 😊. Recuerda que esta información es solo orientativa y no reemplaza la atención médica profesional."
        else:
            response = "Entiendo lo que dices. ¿Podrías especificar si presentas algún síntoma como dolor, sangrado, bultos, tos persistente, etc.?"

    # Añadir descargo de responsabilidad siempre
    response += " ⚠️ Esto no sustituye una consulta médica. Te recomiendo visitar a un profesional de la salud."

    session["historia"].append({"bot": response})

    return jsonify({"response": response, "historia": session["historia"]})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

