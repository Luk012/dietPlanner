const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

let isProfileCreated = false;
let isFirstMessage = true;
let lastQuestion = '';

function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = content;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    if (role === 'assistant' && !isProfileCreated) {
        const clarifyButton = document.createElement('button');
        clarifyButton.textContent = "Ask for clarification";
        clarifyButton.onclick = () => {
            const clarificationPrompt = prompt("What would you like clarified about the question?");
            if (clarificationPrompt) {
                requestClarification(content, clarificationPrompt);
            }
        };
        chatContainer.appendChild(clarifyButton);
    }
}

function showWaitingAnimation() {
    const waitingDiv = document.createElement('div');
    waitingDiv.className = 'waiting';
    waitingDiv.innerHTML = '<div class="dot-flashing"></div>';
    chatContainer.appendChild(waitingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function hideWaitingAnimation() {
    const waitingDiv = document.querySelector('.waiting');
    if (waitingDiv) {
        waitingDiv.remove();
    }
}

function requestClarification(question, clarificationPrompt) {
    showWaitingAnimation();
    fetch('/get_clarification', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question, clarificationPrompt})
    })
    .then(response => response.json())
    .then(data => {
        hideWaitingAnimation();
        addMessage('assistant', data.response);
    });
}

function sendMessage() {
    const message = userInput.value.trim();
    if (message) {
        addMessage('user', message);
        userInput.value = '';
        showWaitingAnimation();

        if (!isProfileCreated) {
            fetch('/create_profile', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: message, lastQuestion: lastQuestion})
            })
            .then(response => response.json())
            .then(data => {
                hideWaitingAnimation();
                addMessage('assistant', data.response);
                lastQuestion = data.response;
                if (data.profileComplete) {
                    isProfileCreated = true;
                }
            });
        } else {
            fetch('/get_meal_suggestion', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: message})
            })
            .then(response => response.json())
            .then(data => {
                hideWaitingAnimation();
                addMessage('assistant', data.suggestion);
            });
        }
    }
}

sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

window.addEventListener('load', () => {
    showWaitingAnimation();
    fetch('/create_profile', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: '', lastQuestion: ''})
    })
    .then(response => response.json())
    .then(data => {
        hideWaitingAnimation();
        addMessage('assistant', data.response);
        lastQuestion = data.response;
    });
});