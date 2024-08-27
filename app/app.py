from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)


# Load the JSON data from the file
def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as json_file:
        return json.load(json_file)


# Function to search the JSON data for relevant information based on the user's query
def search_law(query, document_data):
    results = []

    # Searching the "Unmatched" section for the query
    for line in document_data.get('Unmatched', []):
        if query.lower() in line.lower():
            results.append(line)

    if results:
        return results
    else:
        return ["Sorry, I couldn't find any relevant information on that topic."]


# Load the document data once at startup
document_data = load_json_data('document_structure.json')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    search_results = search_law(user_input, document_data)

    if len(search_results) == 1:
        response = {
            "section": "Relevant Information",
            "content": search_results[0]
        }
    elif len(search_results) > 1:
        response = {
            "section": "Multiple References Found",
            "content": "\n".join(search_results)
        }
    else:
        response = {
            "section": "No Information Found",
            "content": search_results[0]
        }

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
