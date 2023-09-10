from flask import Flask, render_template, request, jsonify
from transformers import GPT2Tokenizer, GPT2LMHeadModel

app = Flask(__name__)

# Load the GPT-2 model and tokenizer
model_name = "gpt2-medium"
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)


# Function to load Q&A pairs from the file
def load_qa_pairs(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    qa_dict = {}
    for i in range(0, len(lines) - 1, 2):  # Iterate over lines in steps of 2
        question = lines[i].strip().replace("Q: ", "")
        answer = lines[i + 1].strip().replace("A: ", "")
        qa_dict[question] = answer
    return qa_dict


# Load the Q&A pairs
qa_dict = load_qa_pairs("law-qa.txt")


# Function to fetch answers from Q&A dict
def get_answer_from_qa_dict(question):
    return qa_dict.get(question, None)


@app.route('/')
def index():
    return render_template('index.html')


def remove_repeated_sentences(text):
    sentences = text.split('.')
    cleaned_sentences = []
    for idx, sentence in enumerate(sentences[:-1]):  # ignore the last sentence (as it's likely cut-off)
        if sentence != sentences[idx + 1]:
            cleaned_sentences.append(sentence)
    return '.'.join(cleaned_sentences) + '.'  # append a period for formatting


@app.route('/ask', methods=['POST'])
def ask():
    message = request.form['message']

    # Check if the question exists in the Q&A dictionary
    direct_answer = get_answer_from_qa_dict(message)
    if direct_answer:
        return jsonify({'message': direct_answer})

    # If not found in Q&A dictionary, generate an answer with GPT-2
    input_ids = tokenizer.encode(message, return_tensors="pt")
    response_ids = model.generate(input_ids,
                                  max_length=100,
                                  temperature=0.8,
                                  num_beams=5,
                                  top_k=40,
                                  top_p=0.95,
                                  no_repeat_ngram_size=2,
                                  early_stopping=True,
                                  pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(response_ids[0], skip_special_tokens=True)
    refined_response = remove_repeated_sentences(response)

    return jsonify({'message': refined_response})


if __name__ == '__main__':
    app.run(debug=True)
