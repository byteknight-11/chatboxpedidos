document.getElementById("send").addEventListener("click", function () {
    sendMessage();
});

// Agregar el evento para enviar con "Enter"
document.getElementById("userInput").addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        event.preventDefault(); // Evita el salto de línea
        sendMessage(); // Llama a la función para enviar el mensaje
    }
});

// Función para enviar el mensaje (reutilizable)
function sendMessage() {
    let input = document.getElementById("userInput").value;
    let chat = document.getElementById("chat");
    
    if (input.trim() === "") return; // Evita enviar mensajes vacíos

    chat.innerHTML += `<p><strong>Tú:</strong> ${input}</p>`;

    fetch("https://chatbot-pedidos.onrender.com", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input })
    })
    .then(response => response.json())
    .then(data => {
        chat.innerHTML += `<p><strong>Asistente virtual:</strong> ${data.response}</p>`;
    });

    document.getElementById("userInput").value = "";
}
