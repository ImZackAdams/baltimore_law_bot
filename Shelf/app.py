import os
from flask import Flask, request, jsonify, render_template
from transformers import BertTokenizer, BertForQuestionAnswering
import torch
import nltk
from nltk.corpus import wordnet
import random

nltk.download('wordnet')

app = Flask(__name__)

# Load pre-trained model and tokenizer
model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"
model = BertForQuestionAnswering.from_pretrained(model_name)
tokenizer = BertTokenizer.from_pretrained(model_name)

# Load context once during app initialization
with open(os.path.join(os.getcwd(), "../law-qa.txt"), 'r') as f:
    context = f.read()


@app.route('/')
def home():
    return render_template('index.html')


# Load pre-trained model and tokenizer
model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"
model = BertForQuestionAnswering.from_pretrained(model_name)
tokenizer = BertTokenizer.from_pretrained(model_name)


def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    if word in synonyms:
        synonyms.remove(word)
    return list(synonyms)


def replace_with_synonyms(sentence):
    words = sentence.split()
    if not words:
        return sentence

    # Randomly select a word
    word_to_replace = random.choice(words)

    # Get synonyms for the word
    synonyms = get_synonyms(word_to_replace)

    # If synonyms are found, replace the original word with a synonym
    if synonyms:
        replacement = random.choice(synonyms)
        sentence = sentence.replace(word_to_replace, replacement, 1)

    return sentence


def filter_answer(answer):
    # Remove special tokens
    return answer.replace("[CLS]", "").replace("[SEP]", "").strip()


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
        answer = filter_answer(answer)  # Filtering the answer here
        score = torch.max(answer_start_scores).item() + torch.max(answer_end_scores).item()

        answers.append((answer, score))

    # Sort answers based on score
    answers.sort(key=lambda x: x[1], reverse=True)

    best_answer = answers[0][0]

    # If answer is empty, too short, or contains only special tokens, default to a generic message
    if len(best_answer.strip()) < 3 or best_answer in ["[CLS]", "[SEP]"]:
        return "I'm sorry, I couldn't find a specific answer to your question. Please rephrase or ask another question."

    return best_answer


@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.json.get("message", "")
    if not user_question:
        return jsonify({"error": "No message provided"}), 400

    user_question_augmented = replace_with_synonyms(user_question)
    answer = get_answer(user_question_augmented, context)
    return jsonify({"answer": answer})


@app.errorhandler(400)
def bad_request(e):
    app.logger.error(f"Bad request: {e.description}")
    return jsonify(error=str(e.description)), 400


if __name__ == '__main__':
    app.run(debug=True)