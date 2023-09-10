from flask import Flask, request, jsonify, render_template
from transformers import BertTokenizer, BertForQuestionAnswering
import torch

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


# Load pre-trained model and tokenizer
model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"
model = BertForQuestionAnswering.from_pretrained(model_name)
tokenizer = BertTokenizer.from_pretrained(model_name)


def get_answer(question, context):
    # Split context into paragraphs
    paragraphs = context.split('\n\n')

    answers = []

    for paragraph in paragraphs:
        inputs = tokenizer(question, paragraph, return_tensors="pt", max_length=512, truncation=True)
        input_ids = inputs["input_ids"].tolist()[0]

        outputs = model(**inputs)
        answer_start_scores = outputs.start_logits
        answer_end_scores = outputs.end_logits

        answer_start = torch.argmax(answer_start_scores)
        answer_end = torch.argmax(answer_end_scores) + 1

        answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))
        score = torch.max(answer_start_scores).item() + torch.max(answer_end_scores).item()

        answers.append((answer, score))

    # Sort answers based on score
    answers.sort(key=lambda x: x[1], reverse=True)

    best_answer = answers[0][0]

    # If answer is empty or too short, default to a generic message
    if len(best_answer.strip()) < 3:
        return "I'm sorry, I couldn't find a specific answer to your question. Please rephrase or ask another question."

    return best_answer


@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.json["message"]

    # Assuming all questions from the law-qa.txt will be used as context.
    with open("law-qa.txt", 'r') as f:
        context = f.read()

    answer = get_answer(user_question, context)
    return jsonify({"answer": answer})


@app.errorhandler(400)
def bad_request(e):
    app.logger.error(f"Bad request: {e.description}")
    return jsonify(error=str(e.description)), 400


if __name__ == '__main__':
    app.run(debug=True)
