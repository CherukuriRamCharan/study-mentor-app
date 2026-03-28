from flask import Flask, request, jsonify
import ollama

app = Flask(__name__)

chat_history = []

SYSTEM_PROMPT = """You are a friendly Study Mentor and Homework Assistant.
- Explain concepts clearly using simple language and examples
- Solve math problems step-by-step
- Help with any school subject: math, science, history, English
- Give essay writing tips
- Be encouraging and patient with students
Keep responses concise but complete."""

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Study Mentor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f4ff; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .chat-container { width: 680px; height: 600px; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); display: flex; flex-direction: column; overflow: hidden; }
        .header { background: #5340b7; color: white; padding: 16px 20px; display: flex; align-items: center; gap: 12px; }
        .header h2 { font-size: 18px; }
        .header p { font-size: 12px; opacity: 0.8; }
        .chat-window { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
        .msg { display: flex; gap: 10px; max-width: 85%; }
        .msg.user { align-self: flex-end; flex-direction: row-reverse; }
        .bubble { padding: 10px 14px; border-radius: 14px; font-size: 14px; line-height: 1.6; }
        .msg.bot .bubble { background: #f0f4ff; color: #333; border-bottom-left-radius: 4px; }
        .msg.user .bubble { background: #5340b7; color: white; border-bottom-right-radius: 4px; }
        .icon { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0; margin-top: 2px; }
        .bot-icon { background: #eeedfe; }
        .user-icon { background: #5340b7; }
        .input-row { display: flex; gap: 8px; padding: 16px; border-top: 1px solid #eee; }
        input { flex: 1; padding: 10px 14px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; }
        input:focus { border-color: #5340b7; }
        button { background: #5340b7; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-size: 14px; cursor: pointer; }
        button:hover { background: #3c3489; }
        button:disabled { background: #aaa; cursor: not-allowed; }
        .typing { display: flex; gap: 4px; align-items: center; padding: 10px 14px; }
        .dot { width: 7px; height: 7px; border-radius: 50%; background: #aaa; animation: bounce 1.2s infinite; }
        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-6px)} }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">
            <div class="icon bot-icon">&#128218;</div>
            <div>
                <h2>Study Mentor</h2>
                <p>Homework helper &middot; Powered by Phi-3 Local AI</p>
            </div>
        </div>
        <div class="chat-window" id="chat">
            <div class="msg bot">
                <div class="icon bot-icon">&#128218;</div>
                <div class="bubble">Hi! I am your Study Mentor. Ask me anything about homework, math, science, history, or essay tips!</div>
            </div>
        </div>
        <div class="input-row">
            <input type="text" id="userInput" placeholder="Ask your question here..." />
            <button id="sendBtn">Send</button>
        </div>
    </div>

    <script>
        var input = document.getElementById('userInput');
        var btn = document.getElementById('sendBtn');
        var chat = document.getElementById('chat');

        btn.addEventListener('click', sendMessage);
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') { sendMessage(); }
        });

        function sendMessage() {
            var text = input.value.trim();
            if (!text) return;
            input.value = '';
            btn.disabled = true;

            var userDiv = document.createElement('div');
            userDiv.className = 'msg user';
            userDiv.innerHTML = '<div class="icon user-icon">&#128587;</div><div class="bubble">' + text + '</div>';
            chat.appendChild(userDiv);

            var typingDiv = document.createElement('div');
            typingDiv.className = 'msg bot';
            typingDiv.id = 'typing';
            typingDiv.innerHTML = '<div class="icon bot-icon">&#128218;</div><div class="bubble"><div class="typing"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div></div>';
            chat.appendChild(typingDiv);
            chat.scrollTop = chat.scrollHeight;

            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            })
            .then(function(res) { return res.json(); })
            .then(function(data) {
                var t = document.getElementById('typing');
                if (t) { t.remove(); }
                var botDiv = document.createElement('div');
                botDiv.className = 'msg bot';
                botDiv.innerHTML = '<div class="icon bot-icon">&#128218;</div><div class="bubble">' + data.reply.replace(/\\n/g, '<br>') + '</div>';
                chat.appendChild(botDiv);
                chat.scrollTop = chat.scrollHeight;
                btn.disabled = false;
                input.focus();
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_PAGE

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json['message']
    chat_history.append({"role": "user", "content": user_msg})
    response = ollama.chat(
        model="tinyllama",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + chat_history
    )
    reply = response["message"]["content"]
    chat_history.append({"role": "assistant", "content": reply})
    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(debug=True)