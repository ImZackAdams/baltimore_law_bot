from flask import Flask, render_template, request, jsonify
from transformers import GPT2Tokenizer, GPT2LMHeadModel

app = Flask(__name__)

# Load the GPT-2 model and tokenizer
model_name = "gpt2-large"
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)


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

    input_ids = tokenizer.encode(message, return_tensors="pt")

    # Enhancing the model generation
    response_ids = model.generate(
        input_ids,
        max_length=150,
        temperature=0.8,
        repetition_penalty=1.2,
        pad_token_id=tokenizer.eos_token_id
    )

    response = tokenizer.decode(response_ids[0], skip_special_tokens=True)
    refined_response = remove_repeated_sentences(response)

    return jsonify({'message': refined_response})


if __name__ == '__main__':
    app.run(debug=True)
