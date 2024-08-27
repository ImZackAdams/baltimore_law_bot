from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# Load the structured document data
with open('document_structure.json', 'r') as json_file:
    document_structure = json.load(json_file)


def search_document(query, document_structure):
    for division, subtitles in document_structure.items():
        for subtitle, sections in subtitles.items():
            if query.lower() in subtitle.lower():
                return subtitle, sections
            for section, content in sections.items():
                if query.lower() in section.lower() or query.lower() in content.lower():
                    return section, content
    return None, "No relevant content found."


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")

    # Search the document based on the user's query
    section, content = search_document(user_message, document_structure)

    response = {
        "section": section,
        "content": content
    }

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
