import os
from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Necesario para manejar sesión en Flask

# --- Base de datos médica ---
symptoms_db = {
    "cáncer de mama": {
        "síntomas": [
            "bulto en el seno", "bulto en la axila", "cambios en el pezón",
            "secreción anormal del pezón", "piel enrojecida en el seno"
        ],
        "mensaje": "El cáncer de mama puede detectarse tempranamente con autoexamen y mamografía."
    },
    "cáncer de pulmón": {
        "síntomas": [
            "tos persistente", "tos con sangre", "dolor en el pecho",
            "dificultad para respirar", "pérdida de peso inexplicada"
        ],
        "mensaje": "El cáncer de pulmón suele estar asociado al tabaco, pero también puede aparecer en no fumadores."
    },
    "cáncer de colon": {
        "síntomas": [
            "cambios en el hábito intestinal", "sangrado rectal",
            "dolor abdominal persistente", "anemia inexplicada"
        ],
        "mensaje": "El cáncer de colon puede prevenirse con chequeos regulares y colonoscopías."
    },
    "cáncer de piel": {
        "síntomas": [
            "lunar con bordes irregulares", "cambio de color en la piel",
            "mancha que crece", "lesión que sangra o no cicatriza"
        ],
        "mensaje": "El cáncer de piel puede prevenirse evitando la exposición excesiva al sol y usando protector solar."
    },
    "cáncer de próstata": {
        "síntomas": [
            "dificultad al orinar", "dolor en la pelvis",
            "sangre en la orina", "flujo urinario débil"
        ],
        "mensaje": "El cáncer de próstata es común en hombres mayores y puede detectarse con un examen de PSA."
    },
    "cáncer de estómago": {
        "síntomas": [
            "acidez persistente", "dolor estomacal crónico",
            "vómitos con sangre", "pérdida de apetito"
        ],
        "mensaje": "El cáncer de estómago puede estar relacionado con la infección por H. pylori y la dieta."
    },
    "leucemia": {
        "síntomas": [
            "fatiga extrema", "infecciones frecuentes",
            "moretones fáciles", "sangrado de encías", "fiebre sin causa aparente"
        ],
        "mensaje": "La leucemia afecta la producción de glóbulos en la médula ósea y requiere estudios de sangre para detectarla."
    },
    "cáncer de hígado": {
        "síntomas": [
            "piel amarillenta", "dolor en la parte superior derecha del abdomen",
            "hinchazón abdominal", "pérdida de peso rápida"
        ],
        "mensaje": "El cáncer de hígado suele estar relacionado con la cirrosis y la hepatitis crónica."
    }
}

# Preguntas frecuentes
faq_db = {
    "qué es el cáncer": "El cáncer es un conjunto de enfermedades donde las células crecen de manera descontrolada y pueden invadir otros tejidos.",
    "cómo se previene el cáncer": "Manteniendo una dieta saludable, evitando el tabaco y alcohol, ejercitándose regularmente y haciéndose chequeos médicos.",
    "qué pruebas existen": "Depende del tipo de cáncer. Existen mamografías, colonoscopías, tomografías, resonancias, análisis de sangre y biopsias.",
    "cuándo ir al médico": "Siempre que tengas síntomas persistentes como dolor, sangrado, bultos, fiebre inexplicada o pérdida de peso sin motivo."
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
            body { font-family: Arial, sans-serif; background: #f4f6f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .chat-container { width: 480px; background: #fff; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: flex; flex-direction: column; overflow: hidden; }
            .chat-header { background: #4CAF50; color: #fff; padding: 15px; text-align: center; font-size: 18px; }
            #chat-box { flex: 1; padding: 10px; overflow-y: auto; background: #fafafa; }
            .user { color: #2196F3; margin: 8px 0; }
            .bot { color: #4CAF50; margin: 8px 0; }
            .input-container { display: flex; border-top: 1px solid #ddd; }
            input { flex: 1; padding: 10px; border: none; outline: none; }
            button { padding: 10px 15px; border: none; background: #4CAF50; color: #fff; cursor: pointer; }
            button:hover { background: #45a049; }
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

    session["historia"].append({"usuario": user_message})
    response = ""

    # Revisar preguntas frecuentes
    for key, answer in faq_db.items():
        if key in user_message:
            response = answer
            break

    # Revisar síntomas y cánceres
    if response == "":
        for cancer, data in symptoms_db.items():
            if cancer in user_message:
                response = f"El {cancer} puede presentar síntomas como: {', '.join(data['síntomas'])}. {data['mensaje']}"
                break
            for s in data["síntomas"]:
                if s in user_message:
                    response = f"El síntoma que mencionas ('{s}') puede estar relacionado con el {cancer}. {data['mensaje']}"
                    break

    # Conversaciones comunes
    if response == "":
        if "hola" in user_message or "buenas" in user_message:
            response = "¡Hola! Soy tu asistente médico virtual. ¿Tienes algún síntoma o pregunta sobre el cáncer?"
        elif "gracias" in user_message:
            response = "Con gusto 😊. Recuerda que esta información es solo orientativa y no reemplaza la atención médica profesional."
        elif "adiós" in user_message or "chau" in user_message:
            response = "Ha sido un placer ayudarte. ¡Cuida tu salud y hasta pronto!"
        else:
            response = "Entiendo lo que dices. ¿Podrías especificar mejor tu síntoma o tu duda? Por ejemplo: 'Tengo sangrado rectal' o '¿Qué es el cáncer de mama?'."

    response += " ⚠️ Esto no sustituye una consulta médica. Te recomiendo visitar a un profesional de la salud."
    session["historia"].append({"bot": response})

    return jsonify({"response": response, "historia": session["historia"]})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
