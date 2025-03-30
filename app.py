#ImportarLibrerias Flask, MongoDB y Re para encontrar los números en los mensajes del usuario ejemplo ID PEDIDO o Identificación del usuario
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import re 

app = Flask(__name__)
CORS(app)

#ConectarConMango DB
client = MongoClient("mongodb+srv://leoeljadues:<db_2CELcb7luLAyxSvr>@cluster0.6q2p56w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["chatbot_db"]
messages_collection = db["messages"]
orders_collection = db["orders"]
learned_responses_collection = db["learned_responses"]

#Variable para declarar si el chatbot espera un id o ya tiene uno previo
user_states = {}

#Respuestas Predeterminadas
responses = {
    "hola": "¡Hola! seré tu asistente virtual, puedes consultar el estado de tu pedido colocando tu número de identificación o identificación del pedido",
    "adiós": "¡Hasta luego!",
    "cómo estás": "Soy un asistente virtual, pero estoy aquí para ayudarte.",
    "default": "Lo siento, no entiendo esa pregunta. ¿Puedes enseñarme la respuesta? puedes hacerlo colocando: `aprende [pregunta] = respuesta`"
}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_id = data.get("user_id", "default_user")  # Para manejar múltiples usuarios
    user_message = data.get("message", "").strip().lower()

    # Si el usuario está en modo de consulta de pedido, esperar un ID
    if user_states.get(user_id) == "waiting_for_order_id":
        user_states[user_id] = None  #Reinicia la consulta si ya se coloco un ID
        return check_order_status(user_message)

    # Si el usuario responde "sí" para consultar otro pedido, pedirle que ingrese otro ID
    if user_message in ["sí", "si"]:
        user_states[user_id] = "waiting_for_order_id"
        return jsonify({"response": "¡Genial! Ingresa el ID del pedido que deseas consultar."})

    # Si el usuario responde "no", despedirse
    if user_message == "no":
        return jsonify({"response": "¡De acuerdo! Si necesitas más ayuda, aquí estaré."})

    # Detectar un número dentro del mensaje (ej. "pedido 10001" o cédula "1019135095")
    match = re.search(r"\d+", user_message)
    if match:
        order_id = match.group()
        return check_order_status(order_id, user_id)

    # Buscar en respuestas aprendidas
    learned_response = learned_responses_collection.find_one({"question": user_message})
    if learned_response:
        response = learned_response["answer"]
    else:
        # Buscar en respuestas predefinidas
        response = responses.get(user_message, responses["default"])

        # Si no conoce la respuesta, pedir que el usuario enseñe con formato "aprender [pregunta] = [respuesta]"
        if response == responses["default"]:
            return jsonify({"response": response, "learn": True})

    messages_collection.insert_one({"user": user_message, "Asistente Virtual": response})
    return jsonify({"response": response, "learn": False})

@app.route("/order_status", methods=["POST"])
def check_order_status(order_id=None, user_id="default_user"):
   
    #Consulta el estado de un pedido en la base de datos y devuelve la información en formato JSON.
    #Parámetros: order_id (str, opcional): ID del pedido a consultar. Si no se proporciona, se obtiene del JSON recibido.- user_id (str, opcional): Identificador del usuario. No se usa en esta versión.

    if order_id is None:
        data = request.get_json()
        order_id = data.get("order_id", "").strip()
    #Si el pedido existe, informa su estado y tiempo de entrega. Si ya fue entregado, lo indica. 
    order = orders_collection.find_one({"order_id": order_id})
    if order:
        if order['status'].lower() == "entregado":
            response = f"Tu pedido {order_id} ya fue entregado."
      #También pregunta si el usuario quiere consultar otro pedido.    
        else: 
            response = f"Tu pedido {order_id} está {order['status']} y llegará en {order['delivery_time']}."
        response += "\n¿Deseas consultar otro pedido? (Responde 'sí' o 'no')"
    #Si no se encuentra el pedido, devuelve un mensaje de error. 
    else:
        response = "No encontré información sobre ese pedido. Asegúrate de ingresar un ID válido."

    return jsonify({"response": response})


if __name__ == "__main__":
    from os import environ
    port = int(environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)