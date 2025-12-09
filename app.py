from flask import Flask, render_template, request, jsonify
from rag_engine import ask_bot
import time
import random
import os

app = Flask(__name__)

conversation = []
last_time = time.time()
TIMEOUT = 30


def reset_if_inactive():
    global conversation
    time_diff = time.time() - last_time
    if time_diff > TIMEOUT:
        conversation = []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    global conversation, last_time

    reset_if_inactive()

    user_msg = request.form["message"].strip()
    last_time = time.time()

    conversation.append({"role": "user", "text": user_msg})

    greetings = ["hi", "hello", "hey", "yo", "hola"]
    greet_replies = [
        "Hello! How can I assist you today?",
        "Hi there! 😊 What can I help you with?",
        "Hey! Ask me anything."
    ]

    if user_msg.lower() in greetings:
        bot = random.choice(greet_replies)
        conversation.append({"role": "bot", "text": bot})
        return jsonify({"reply": bot})

    short_words = ["ok", "okay", "k", "cool", "nice", "thanks", "thank you"]
    short_replies = [
        "Okay cool! 😊",
        "Great!",
        "Sure, anytime!",
        "Awesome!"
    ]

    if user_msg.lower() in short_words:
        bot = random.choice(short_replies)
        conversation.append({"role": "bot", "text": bot})
        return jsonify({"reply": bot})

    # Normal RAG response
    bot_raw = ask_bot(user_msg)

    ending = random.choice([
        "",
        " Let me know if you want to know more!",
        " Happy to help!",
        " Feel free to ask anything!"
    ])

    if bot_raw.startswith("I don't"):
        final = bot_raw
    else:
        final = bot_raw + ending

    conversation.append({"role": "bot", "text": final})
    return jsonify({"reply": final})


# -------- Render PORT binding --------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
