from flask import Blueprint, render_template, request, jsonify
from app.models.embeddings import model, qa_model, tokenizer, answer_question, create_combined_embeddings
from app.utils.query_handling import handle_user_query
from .shared import main_law_text

# Create a blueprint
views = Blueprint('views', __name__)

# Split the main law text into sentences or paragraphs for simplicity.
sentences = main_law_text.split(".")

# Create embeddings
embeddings = create_combined_embeddings(sentences)


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
    best_section_title, best_section_subtitle, response = handle_user_query(message, main_law_text,)

    # Return the response as JSON. Include title and subtitle if needed.
    return jsonify({'answer': response, 'section_title': best_section_title, 'section_subtitle': best_section_subtitle})


@views.route('/answer', methods=['POST'])
def get_answer():
    query = request.form.get('query')

    if not query:
        return jsonify({"error": "Query not provided."}), 400

    # Adjust here as well to handle three return values
    best_section_title, best_section_subtitle, best_answer = handle_user_query(query, main_law_text)

    return jsonify(
        {"section_title": best_section_title, "section_subtitle": best_section_subtitle, "answer": best_answer})
