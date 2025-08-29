import os
from flask import Flask, request, jsonify, session
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Inicializar cliente OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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


@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Chatbot Médico con IA</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f6f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .chat-container { width: 500px; background: #fff; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: flex; flex-direction: column; overflow: hidden; }
            .chat-header { background: #6A1B9A; color: #fff; padding: 15px; text-align: center; font-size: 18px; }
            #chat-box { flex: 1; padding: 10px; overflow-y: auto; background: #fafafa; }
            .user { color: #2196F3; margin: 8px 0; }
            .bot { color: #6A1B9A; margin: 8px 0; }
            .input-container { display: flex; border-top: 1px solid #ddd; }
            input { flex: 1; padding: 10px; border: none; outline: none; }
            button { padding: 10px 15px; border: none; background: #6A1B9A; color: #fff; cursor: pointer; }
            button:hover { background: #4A148C; }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">🤖 Chatbot Médico con IA</div>
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


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").lower()
    response = ""

    # --- Lógica fija de síntomas ---
    for cancer, data in symptoms_db.items():
        if cancer in user_message:
            response = f"El {cancer} puede presentar síntomas como: {', '.join(data['síntomas'])}. {data['mensaje']}"
            break
        for s in data["síntomas"]:
            if s in user_message:
                response = f"El síntoma '{s}' puede estar relacionado con el {cancer}. {data['mensaje']}"
                break

    # --- Si no hay respuesta fija, usar IA ---
    if response == "":
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # puedes cambiar por otro modelo más económico
            messages=[
                {"role": "system", "content": "Eres un asistente médico virtual. Orienta sobre síntomas, prevención y hábitos saludables, pero nunca reemplaces al médico."},
                {"role": "user", "content": user_message}
            ]
        )
        response = completion.choices[0].message.content

    # Descargo de responsabilidad siempre
    response += "\n\n⚠️ Nota: Esta información es solo orientativa y no reemplaza una consulta médica profesional."

    return jsonify({"response": response})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
