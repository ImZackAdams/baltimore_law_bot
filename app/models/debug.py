from embeddings import tokenizer, answer_question, debug_tokenization
from app.utils.pdf_processing import extract_text_from_pdf, clean_text


def debug_bert():
    test_question = "Who was president of the US in 2021?"
    test_context = "In 2021, Joe Biden became the president of the US after winning the 2020 elections."
    test_answer = answer_question(test_question, test_context)
    print(test_answer)  # Expected: "Joe Biden"


def debug_with_chunks(context):
    chunks = debug_tokenization("affordable housing", context)

    for i, chunk in enumerate(chunks):
        print(f"Chunk {i + 1}: {tokenizer.convert_tokens_to_string(chunk)}")
        sample_answer = answer_question("affordable housing", tokenizer.convert_tokens_to_string(chunk))
        print(f"Answer from chunk {i + 1}: {sample_answer}")
        print('-' * 50)


if __name__ == "__main__":
    # Extract the content of your legal document from the PDF, clean it, and use it as the context
    raw_context = extract_text_from_pdf('legaldocs/Article-13-housing.pdf')
    context = clean_text(raw_context)

    print("Debugging BERT on a simple test...")
    debug_bert()

    print("\nDebugging with Chunks...")
    debug_with_chunks(context)
