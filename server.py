from flask import Flask, request, jsonify

app = Flask(__name__)

# Ruta principal con interfaz web del chatbot
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
                width: 400px;
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

# API de chatbot
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    # Respuesta básica
    if "cáncer" in user_message.lower():
        respuesta = "El cáncer presenta diferentes síntomas según el tipo: fatiga, bultos, pérdida de peso inexplicada, sangrado anormal, entre otros. ¿Quieres que te dé información más detallada de un tipo específico?"
    else:
        respuesta = "Soy un asistente médico y puedo orientarte sobre síntomas de cáncer. Por favor, dime qué quieres saber."

    return jsonify({"response": respuesta})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
