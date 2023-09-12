from flask import render_template, request, jsonify

# Import relevant modules and functions
from app.models.embeddings import model, qa_model, tokenizer, answer_question, create_combined_embeddings
from app.utils.pdf_processing import extract_text_from_pdf, clean_text
from app.utils.text_utils import extract_content_from_section, retrieve_top_n_sections, is_unsatisfactory, reformulate_query
from app.utils.query_handling import handle_user_query

# Assuming the Flask app instance is initialized in a file named app.py or __init__.py and not directly here
from app import app


@app.route('/')
def index():
    """Renders the main page."""
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.json.get('message')

    # Process the user_message using your chatbot logic
    response = handle_user_query(user_message)

    # Assuming response is a tuple of (best_section, best_answer)
    _, best_answer = response  # We are only using the answer part here.

    # Return the answer
    return jsonify(answer=best_answer)


@app.route('/answer', methods=['POST'])
def get_answer():
    """Handles user query and returns the best answer."""
    query = request.form['query']

    # Placeholder logic to process the query and determine best_answer and best_section
    # This logic should ideally be broken out into helper functions or methods, but for simplicity's sake, I'm placing it here.
    best_answer = "Your best answer will be determined here"
    best_section = "The relevant section will be identified here"
    # ... (rest of the code related to user query handling)

    # Instead of print, send the results back to the client using render_template or jsonify
    return render_template('answer.html', section=best_section, answer=best_answer)




# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handles 404 errors and renders a custom page."""
    app.logger.error(f"Page not found: {request.url}")
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Handles internal server errors and renders a custom page."""
    app.logger.error(f"Internal server error: {e}")
    return render_template('500.html'), 500



if __name__ == '__main__':
    app.run(debug=True)
