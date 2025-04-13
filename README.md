# chatboxpedidos(https://byteknight-11.github.io/chatboxpedidos/)

 Montaje del Proyecto: Chatbot de Consulta de Pedidos
1. Planteamiento de la Idea
El objetivo del proyecto es simular un sistema de consulta de pedidos de plataformas como Amazon o MercadoLibre, donde el usuario ingresa su ID de pedido o cédula y permite consultar el estado, siendo capaz de responder preguntas generales y si no conoce lo que el usuario escribe debe permitirleaprender nuevas respuestas.

Ejemplo sobre el flujo de la conversación sería:
1. El usuario saluda, el chatbot responde y explica su función.
2. El usuario ingresa su número de pedido, el chatbot consulta la base de datos y devuelve el estado.
3. Si el usuario pregunta algo que el bot no sabe → el chatbot aprende una nueva respuesta si se le enseña.

2. Backend: Creación del Chatbot con Flask y MongoDB
El backend se desarrolló con Python (Flask) para manejar las solicitudes del usuario y MongoDB para consultar los pedidos y respuestas aprendidas.

 -Creación del Servidor donde Flask inicializa el servidor y CORS permite que el frontend pueda hacer peticiones:


	app = Flask(__name__)
	CORS(app)




- Conexión con la Base de Datos Se obtiene la URI de MongoDB desde una variable de entorno MONGO_URI en Render para tener acceso a la información de los pedidos.

	MONGO_URI = os.getenv("MONGO_URI")
	client = MongoClient(MONGO_URI)
	db = client["chatbot_db"]
	orders_collection = db["orders"]


- Consultar Estado de un Pedido buscandolo en la base de MangoDB, donde, si existe devuelve su estado y tiempo de entrega y si no, le pide un ID válido para consultar.

	@app.route("/order_status", methods=["POST"])
	def check_order_status():
    	data = request.get_json()
    	order_id = data.get("order_id", "").strip()
    	order = orders_collection.find_one({"order_id": order_id})

    	if order:
        	response = f"Tu pedido {order_id} está {order['status']} y llegará en {order['delivery_time']}."
    	else:
        	response = "No encontré información sobre ese pedido."

    	return jsonify({"response": response})

3.Frontend: Interfaz de Usuario con HTML, CSS y JavaScript


- Envío de Mensajes al Backend, enviando mensajes al servidor Flask mediante Fetch API  y el el backend responde con la información del pedido o una respuesta general.

	fetch("https://chatbot-pedidos.onrender.com/chat", {
    	method: "POST",
    	headers: { "Content-Type": "application/json" },
    	body: JSON.stringify({ message: input })
	})




-Mostrar el Mensaje en la Pantalla

	chat.innerHTML += `<p><strong>Asistente virtual:</strong> ${data.response}</p>`;
	Agrega la respuesta del chatbot al historial de conversación.


4. Herramientas Utilizadas:

 - Flask (Framework de Python para crear la API.)
 - MongoDB Atlas (Base de datos en la nube.)
 - JavaScript ( Manejo del frontend y conexión con Flask.)
 - HTML y CSS  (Creación de la interfaz de usuario.)
 - Render (Despliegue del backend.)
 - GitHub Pages ( Publicación de la interfaz web.)

5. Despliegue y Uso
Para que cualquier persona pueda usar el chatbot:
 - El backend se desplegó en Render.
 - La interfaz web se subió a GitHub Pages.

6. Este proyecto se alinea con la estructura SOA porque:

-El backend está diferenciado del frontend.

-Cada funcionalidad (consultar pedido, responder preguntas generales, aprender nuevas respuestas) está separada en funciones especificas.

-El sistema es modular y escalable, lo que permite agregar nuevos servicios sin afectar los existentes.

-La capacidad del chatbot para aprender nuevas respuestas está agregada como un servicio independiente, que permite guardar preguntas y respuestas enseñadas por el usuario, para que puedan ser usadas en futuras conversaciones.


Cualquier usuario puede acceder a la página web y consultar su pedido ingresando su ID de pedido en el chat, la url es https://byteknight-11.github.io/chatboxpedidos/
