from flask import Blueprint, render_template, request, jsonify

# Create a blueprint
views = Blueprint('views', __name__)


@views.route('/')
def index():
    return render_template('index.html')


@views.route('/ask', methods=['POST'])
def ask():
    # Get the message from the POST request
    message = request.json['message']

    if not message:
        return jsonify({'answer': 'Please provide a question.'}), 400

    # Here, you would use your chatbot logic to generate a response.
    # For the sake of this example, I'm just echoing back the same message:
    response = f"You asked: {message}"

    # Return the response as JSON
    return jsonify({'answer': response})


@views.route('/answer', methods=['POST'])
def get_answer():
    # Your existing logic for the /answer route
    query = request.form.get('query')
    if not query:
        return render_template('error.html', error_message="Query not provided.")

    # Placeholder response:
    return render_template('answer.html', section="Sample Section", answer="Sample Answer based on the query.")
