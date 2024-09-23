// chatbot.js

// Función para enviar mensajes al servidor
function sendMessage() {
    const userInput = document.getElementById('userInput').value;
    if (userInput.trim() !== '') {
        // Agrega el mensaje del usuario al chatbot
        document.getElementById('chatbotBody').innerHTML += `<div class="chat-message">Tú: ${userInput}</div>`;
        
        // Enviar la pregunta al servidor
        fetch('/consulta-chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ pregunta: userInput })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('chatbotBody').innerHTML += `<div class="chat-message">${data.respuesta}</div>`;
        });
        
        document.getElementById('userInput').value = ''; // Limpiar campo de entrada
    }
}

// Función para manejar la selección de opciones
function seleccionarOpcion(animal) {
    const subOpcionesDiv = document.getElementById('subOpciones');
    const mainOptionsDiv = document.getElementById('mainOptions');
    
    mainOptionsDiv.style.display = 'none'; // Ocultar opciones principales
    subOpcionesDiv.style.display = 'grid'; // Mostrar subopciones

    let opcionesHTML = '';
    
    if (animal === 'gato') {
        opcionesHTML = `
            <div class="chatbot-option" onclick="mostrarResultado('Gato enfermo')">Está enfermo</div>
            <div class="chatbot-option" onclick="mostrarResultado('Gato sano')">Está sano</div>
        `;
    } else if (animal === 'perro') {
        opcionesHTML = `
            <div class="chatbot-option" onclick="mostrarResultado('Perro enfermo')">Está enfermo</div>
            <div class="chatbot-option" onclick="mostrarResultado('Perro sano')">Está sano</div>
        `;
    }

    subOpcionesDiv.innerHTML = opcionesHTML;
}

// Función para mostrar el resultado en el chatbot
function mostrarResultado(resultado) {
    const chatbotBody = document.getElementById('chatbotBody');
    chatbotBody.innerHTML += `<div class="chat-message">${resultado}</div>`;
    document.getElementById('subOpciones').style.display = 'none'; // Ocultar subopciones después de seleccionar
    document.getElementById('mainOptions').style.display = 'grid'; // Mostrar opciones principales nuevamente
}
    