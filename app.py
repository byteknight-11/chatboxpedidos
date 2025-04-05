# Importar Librerías Flask, MongoDB y Re para procesar ID de pedidos
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import re
import os

# Inicializar Flask
app = Flask(__name__)
CORS(app)

# Conectar con MongoDB Atlas usando la variable de entorno
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("ERROR: No se encontró la variable de entorno MONGO_URI. Asegúrate de configurarla en Render o localmente.")

try:
    client = MongoClient(MONGO_URI)
    db = client["chatbot_db"]
    messages_collection = db["messages"]
    orders_collection = db["orders"]
    learned_responses_collection = db["learned_responses"]
    print("Conectado a MongoDB correctamente.")
except Exception as e:
    print(f"ERROR al conectar con MongoDB: {e}")
    exit(1)

# Diccionario para el estado del usuario (espera de ID de pedido)
user_states = {}

# Respuestas predeterminadas del chatbot
responses = {
    "hola": "¡Hola! Seré tu asistente virtual. Puedes consultar el estado de tu pedido colocando tu número de identificación o identificación del pedido.",
    "adiós": "¡Hasta luego!",
    "cómo estás": "Soy un asistente virtual, pero estoy aquí para ayudarte.",
    "default": "Lo siento, no entiendo esa pregunta. ¿Puedes enseñarme la respuesta? Puedes hacerlo con: `aprende [pregunta] = respuesta`"
}

# Ruta de prueba para ver si el servidor funciona
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API funcionando. Usa POST en /chat para interactuar."})

# Ruta principal del chatbot
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_id = data.get("user_id", "default_user")
    user_message = data.get("message", "").strip().lower()

    # Verificar si el usuario quiere enseñar una nueva respuesta
    if user_message.startswith("aprende "):
        try:
            parts = user_message.replace("aprende ", "").split("=", 1)
            question = parts[0].strip()
            answer = parts[1].strip()

            if question and answer:
                learned_responses_collection.update_one(
                    {"question": question},
                    {"$set": {"answer": answer}},
                    upsert=True
                )
                return jsonify({"response": f"¡Listo! Ahora sé cómo responder a: '{question}'", "learn": False})
            else:
                return jsonify({"response": "Formato incorrecto. Usa: aprende pregunta = respuesta", "learn": False})
        except Exception:
            return jsonify({"response": "Hubo un problema al aprender la nueva respuesta. Intenta de nuevo.", "learn": False})

    # Verificar si el usuario está esperando ingresar un ID de pedido
    if user_states.get(user_id) == "waiting_for_order_id":
        user_states[user_id] = None
        return check_order_status(user_message)

    # Confirmar si el usuario quiere consultar otro pedido
    if user_message in ["sí", "si"]:
        user_states[user_id] = "waiting_for_order_id"
        return jsonify({"response": "¡Genial! Ingresa el ID del pedido que deseas consultar."})

    # Si el usuario responde "no", despedirse
    if user_message == "no":
        return jsonify({"response": "¡De acuerdo! Si necesitas más ayuda, aquí estaré."})

    # Buscar un número en el mensaje (ej. "pedido 10001")
    match = re.search(r"\d+", user_message)
    if match:
        order_id = match.group()
        return check_order_status(order_id, user_id)

    # Buscar respuesta en la base de datos (respuestas aprendidas)
    learned_response = learned_responses_collection.find_one({"question": user_message})
    if learned_response:
        response = learned_response["answer"]
    else:
        response = responses.get(user_message, responses["default"])

        if response == responses["default"]:
            return jsonify({"response": response, "learn": True})

    # Guardar conversación en la base de datos
    messages_collection.insert_one({"user": user_message, "Asistente Virtual": response})

    return jsonify({"response": response, "learn": False})

# Ruta para consultar el estado de un pedido
@app.route("/order_status", methods=["POST"])
def check_order_status(order_id=None, user_id="default_user"):
    if order_id is None:
        data = request.get_json()
        order_id = data.get("order_id", "").strip()

    order = orders_collection.find_one({"order_id": order_id})

    if order:
        status = order.get("status", "Estado desconocido").lower()
        delivery_time = order.get("delivery_time", "Tiempo desconocido")

        if status == "entregado":
            response = f"Tu pedido {order_id} ya fue entregado."
        else:
            response = f"Tu pedido {order_id} está {status} y llegará en {delivery_time}."

        response += "\n¿Deseas consultar otro pedido? (Responde 'sí' o 'no')"
    else:
        response = "No encontré información sobre ese pedido. Asegúrate de ingresar un ID válido."

    return jsonify({"response": response})

# Configurar Flask para Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Servidor ejecutándose en el puerto {port}")
    app.run(host="0.0.0.0", port=port)


