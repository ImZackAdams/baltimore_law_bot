from flask import Flask, request, jsonify, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chatbot', methods=['POST'])
def chatbot_endpoint():
    data = request.json
    user_message = data.get("message", "")  # getting the user message

    # For now, let's just return the same message to ensure it's working
    response_message = "You said: " + user_message

    return jsonify(response=response_message)


if __name__ == '__main__':
    app.run(debug=True)
