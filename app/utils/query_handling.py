from app.models.embeddings import model, qa_model, tokenizer, answer_question
from app.utils.pdf_processing import extract_text_from_pdf, clean_text
from app.utils.text_utils import extract_content_from_section, retrieve_top_n_sections, is_unsatisfactory, \
    reformulate_query

def handle_user_query(query, main_law_text, embeddings):
    """
    Handle the user's query, extract relevant sections, and get the best answer.

    :param query: The user's question or query.
    :param main_law_text: The main text content to search within.
    :param embeddings: The embeddings of the sections or the entire main_law_text.
    :return: Tuple containing the best section and the best answer.
    """

    # Step 1: Reformulate the user's query if necessary
    refined_query = reformulate_query(query)

    # Initialize best_section and best_answer
    best_section, best_answer = "", ""

    # Step 2: Retrieve top N sections based on the reformulated query and embeddings
    try:
        top_sections = retrieve_top_n_sections(refined_query, embeddings)
    except Exception as e:
        return best_section, f"Error retrieving top sections: {e}"

    # Check if top_sections is empty
    if not top_sections:
        return best_section, "Couldn't identify top sections. Please refine your query."

    # Step 3: For each section, use the QA model to get the answer
    answers = []
    for section in top_sections:
        try:
            # Extract content from the main law text
            content = extract_content_from_section(section, main_law_text)

            # Use QA model to get the answer from the section
            ans = answer_question(qa_model, tokenizer, refined_query, content)

            # If the answer is satisfactory (not just pointing to another division or subtitle), store
            if not is_unsatisfactory(ans):
                answers.append((section, ans))
        except Exception as e:
            # You can also log the error here if needed
            continue  # Move on to the next section if there's an error

    # If we got answers, return the best one (based on some criteria, e.g., length, confidence, etc.)
    if answers:
        best_section, best_answer = max(answers, key=lambda x: len(x[1]))
        return best_section, best_answer

    # If no satisfactory answers were found, return a default message
    return best_section, "Sorry, I couldn't find a relevant answer to your question. Please try rephrasing or asking another question."
