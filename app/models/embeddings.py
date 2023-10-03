import torch
from transformers import BertTokenizer, BertForQuestionAnswering
from sentence_transformers import SentenceTransformer

# Initializations
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
qa_model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')


def answer_question(question, context):
    inputs = tokenizer(question, context, return_tensors="pt", max_length=512, truncation=True)
    print(f"Question: {question}")  # Debug
    print(f"Context Length: {len(context)}")  # Debug

    input_ids = inputs["input_ids"].tolist()[0]
    outputs = qa_model(**inputs)

    answer_start_scores = outputs.start_logits
    answer_end_scores = outputs.end_logits
    answer_start = torch.argmax(answer_start_scores)
    answer_end = torch.argmax(answer_end_scores) + 1

    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))
    print(f"Answer from answer_question: {answer}")  # Debug
    return answer


def create_combined_embeddings(texts):
    embeddings_dict = {}
    for text in texts:
        embeddings_dict[text] = model.encode(text, convert_to_tensor=True)
    return embeddings_dict


def debug_tokenization(question, context):
    chunk_size = 400  # tokens
    overlap = 50  # tokens

    context_tokens = tokenizer.tokenize(context)
    chunk_texts = [context_tokens[i:i + chunk_size] for i in range(0, len(context_tokens), chunk_size - overlap)]

    for idx, chunk in enumerate(chunk_texts):
        chunk_text = tokenizer.convert_tokens_to_string(chunk)
        print(f"Chunk {idx + 1}: {chunk_text[:100]}...")  # Print the beginning of each chunk

    return chunk_texts
