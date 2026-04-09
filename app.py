from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        user_input = request.form.get("user_input")

        # Simple AI logic (you can customize)
        if user_input:
            result = f"You said: {user_input}"

    return render_template("index.html", result=result)

# IMPORTANT: Fix for Render / deployment
if __name__ == "__main__":
    app.run(debug=True)
