import torch
from transformers import BertTokenizer, BertForQuestionAnswering
from sentence_transformers import SentenceTransformer, util

# Initializations
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
qa_model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')


def answer_question(question, context):
    inputs = tokenizer(question, context, return_tensors="pt", max_length=512, truncation=True)
    input_ids = inputs["input_ids"].tolist()[0]

    outputs = qa_model(**inputs)
    answer_start_scores = outputs.start_logits
    answer_end_scores = outputs.end_logits

    answer_start = torch.argmax(answer_start_scores)
    answer_end = torch.argmax(answer_end_scores) + 1

    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))
    # You can further filter or process the answer if needed
    return answer


def create_combined_embeddings(texts):
    # This function takes a list of texts and returns a dictionary where keys are texts and values are embeddings
    embeddings_dict = {}
    for text in texts:
        embeddings_dict[text] = model.encode(text, convert_to_tensor=True)
    return embeddings_dict
