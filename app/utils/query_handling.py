from sentence_transformers import util

from app.models.embeddings import model, qa_model, tokenizer, answer_question  # Adjust imports as necessary
from app.utils.pdf_processing import extract_sections_titles_subtitles
from app.utils.text_utils import retrieve_top_n_sections, is_unsatisfactory, reformulate_query


# ... (Additional imports and other utility functions)

def reformulate_query(query):
    # For now, returning the query unchanged.
    # Implement actual reformulation logic based on your needs.
    return query


def retrieve_top_n_sections(refined_query, embeddings):
    # assuming model is your SentenceTransformer model
    query_embedding = model.encode(refined_query, convert_to_tensor=True)

    print("Query Embedding:", query_embedding)  # Printing Query Embedding

    similarities = []
    for text, embed in embeddings.items():
        print(f"Section: {text}, Embedding: {embed}")  # Printing each section and its embedding
        sim = util.pytorch_cos_sim(query_embedding, embed)  # assuming util is from sentence_transformers
        similarities.append((text, float(sim)))
        print(f"Similarity between {text} and query: {float(sim)}")  # Printing calculated similarity

    sorted_sections = sorted(similarities, key=lambda x: x[1], reverse=True)
    top_sections = [section[0] for section in sorted_sections[:3]]  # assuming you want the top 3 sections

    print(f"Calculated Similarities: {similarities}")  # Printing all calculated similarities
    print(f"Top Sections: {top_sections}")  # Printing the final top sections

    return top_sections


def is_unsatisfactory(ans):
    # For now, returning False.
    # Implement logic to determine whether the provided answer is unsatisfactory.
    return False


def handle_user_query(query, main_law_text, embeddings):
    """
    Handle the user's query, extract relevant sections, and get the best answer.

    :param query: The user's question or query.
    :param main_law_text: The main text content to search within.
    :param embeddings: The embeddings of the sections or the entire main_law_text.
    :return: Tuple containing the best section title, subtitle, and the best answer.
    """
    refined_query = reformulate_query(query)
    print(f"Refined Query: {refined_query}")  # Debug: print refined query

    best_section_title, best_section_subtitle, best_answer = "", "", ""

    try:
        top_sections = retrieve_top_n_sections(refined_query, embeddings)
    except Exception as e:
        print(f"Error retrieving top sections: {e}")  # Debug: print error during top section retrieval
        return best_section_title, best_section_subtitle, f"Error retrieving top sections: {e}"

    if not top_sections:
        print("No top sections identified")  # Debug: print when no top sections are identified
        return best_section_title, best_section_subtitle, "Couldn't identify top sections. Please refine your query."

    # Assuming extract_sections_titles_subtitles is a method that you have to implement to extract the relevant sections
    sections = extract_sections_titles_subtitles(main_law_text)

    answers = []
    for section in sections:
        try:
            title = section['title']
            subtitle = section['subtitle']
            content = section['content']

            ans = answer_question(qa_model, tokenizer, refined_query, content)

            if not is_unsatisfactory(ans):
                answers.append((title, subtitle, ans))
        except Exception as e:
            print(f"Error in processing section: {e}")  # Debug: print error during section processing
            continue  # Move to the next section if there's an error processing the current one

    if answers:
        best_section_title, best_section_subtitle, best_answer = max(answers, key=lambda x: len(x[2]))
        return best_section_title, best_section_subtitle, best_answer

    print("No relevant answer found")  # Debug: print when no relevant answer is found
    return best_section_title, best_section_subtitle, "Sorry, I couldn't find a relevant answer to your question. " \
                                                      "Please try rephrasing or asking another question. "
