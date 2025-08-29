import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Cliente OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Chat Médico Empático</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f6f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .chat-container { width: 500px; background: #fff; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: flex; flex-direction: column; overflow: hidden; }
            .chat-header { background: #1565C0; color: #fff; padding: 15px; text-align: center; font-size: 18px; }
            #chat-box { flex: 1; padding: 10px; overflow-y: auto; background: #fafafa; }
            .user { color: #1E88E5; margin: 8px 0; }
            .bot { color: #1565C0; margin: 8px 0; }
            .input-container { display: flex; border-top: 1px solid #ddd; }
            input { flex: 1; padding: 10px; border: none; outline: none; }
            button { padding: 10px 15px; border: none; background: #1565C0; color: #fff; cursor: pointer; }
            button:hover { background: #0D47A1; }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">🤖 Asistente Médico Empático</div>
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
    user_message = request.json.get("message", "")

    # Llamada a la IA para dar respuesta empática
    completion = client.chat.completions.create(
        model="gpt-4o-mini",  
        messages=[
            {"role": "system", "content": (
                "Eres un asistente médico virtual con un tono empático y humano. "
                "Tu tarea es conversar de forma calmada y sensible con pacientes que expresan síntomas, dudas o temores. "
                "Haz preguntas paso a paso para entender mejor la situación, escucha antes de dar información médica. "
                "Brinda apoyo emocional, reconoce sus sentimientos y explica las cosas con delicadeza. "
                "Siempre sugiere consultar con un médico real, pero nunca ignores lo que la persona siente."
            )},
            {"role": "user", "content": user_message}
        ]
    )

    response = completion.choices[0].message.content
    response += "\n\n⚠️ Nota: Esta conversación es orientativa y no reemplaza la atención médica profesional."

    return jsonify({"response": response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
