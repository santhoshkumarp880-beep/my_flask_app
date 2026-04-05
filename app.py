from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Chat history save globally
chat_history = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global chat_history
    user_message = request.json.get("message").strip()
    lower_msg = user_message.lower()

    # 🔹 Simple AI logic (keyword-based)
    if "hello" in lower_msg:
        reply = "Hi! எப்படி இருக்கீங்க?"
    elif "python" in lower_msg:
        reply = "Python ஒரு popular programming language 🐍"
    elif "ai" in lower_msg:
        reply = "AI (Artificial Intelligence) machines கற்றுக்கொண்டு decision எடுக்கும் திறன்"
    elif "bye" in lower_msg:
        reply = "Bye! நல்ல நாள் 😊"
    elif "javascript" in lower_msg:
        reply = "JavaScript web developmentக்கு main language 🌐"
    else:
        reply = "நான் இன்னும் கற்றுக்கொண்டு இருக்கேன் 🤖"

    # Save to chat history
    chat_history.append({"user": user_message, "ai": reply})

    # Return latest reply + full history
    return jsonify({"response": reply, "history": chat_history})

if __name__ == "__main__":
    app.run(debug=True)