from flask import Blueprint, render_template, request, jsonify
from app.models.embeddings import model, qa_model, tokenizer, answer_question
from app.utils.query_handling import handle_user_query
from . import main_law_text

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

    # Use the handle_user_query function to get the best answer
    _, response = handle_user_query(message, main_law_text, embeddings)

    # Return the response as JSON
    return jsonify({'answer': response})


@views.route('/answer', methods=['POST'])
def get_answer():
    query = request.form.get('query')

    if not query:
        return jsonify({"error": "Query not provided."}), 400

    # For simplicity, let's pass None for embeddings for now
    best_section, best_answer = handle_user_query(query, main_law_text, None)

    return jsonify({"section": best_section, "answer": best_answer})
