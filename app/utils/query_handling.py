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


def handle_user_query(query, main_law_text):
    refined_query = reformulate_query(query)
    print(f"Refined Query: {refined_query}")  # Debug: print refined query

    sections = extract_sections_titles_subtitles(main_law_text)

    best_section_title, best_section_subtitle, best_answer = "", "", ""
    max_confidence = float('-inf')

    for section in sections:
        try:
            title = section['title']
            subtitle = section['subtitle']
            content = section['content']

            # Get the answer and its confidence for the current section
            ans, confidence = answer_question(refined_query, content)

            if confidence > max_confidence:  # Replace with your criteria (e.g., length of answer)
                best_answer = ans
                best_section_title = title
                best_section_subtitle = subtitle
                max_confidence = confidence

        except Exception as e:
            print(f"Error in processing section: {e}")
            continue

    if best_answer:
        return best_section_title, best_section_subtitle, best_answer

    print("No relevant answer found")
    return best_section_title, best_section_subtitle, "Sorry, I couldn't find a relevant answer to your question. Please try rephrasing or asking another question."
