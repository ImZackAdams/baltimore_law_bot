from sentence_transformers import util

from app.models.embeddings import model, qa_model, tokenizer, answer_question  # Adjust imports as necessary
from app.utils.pdf_processing import extract_sections_titles_subtitles
from app.utils.text_utils import retrieve_top_n_sections, is_unsatisfactory, reformulate_query
from .text_utils import split_sections


# ... (Additional imports and other utility functions)

def refine_query(query):
    # For now, we'll return the query as it is. In a more advanced system, you can use SentenceTransformer
    # or another model to find a more refined or similar query from a predefined set.
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
    # Use SentenceTransformer to refine the query
    refined_query = refine_query(query)

    print(f"Refined Query: {refined_query}")

    # Split the main text into sections based on your delimiter (make sure you've defined your split_sections function)
    sections = split_sections(main_law_text)

    answers = []

    # Process each section
    for section in sections:
        try:
            print(f"Processing section: {section}")  # Debug print
            title, subtitle, content = section['title'], section['subtitle'], section['content']

            ans = answer_question(refined_query, content)

            if not is_unsatisfactory(ans):
                answers.append((title, subtitle, ans))

        except Exception as e:
            print(f"Error in processing section: {e}")
            continue

    # After processing all sections, find the best answer
    if answers:
        best_answer = max(answers, key=lambda x: len(x[2]))  # You can use other metrics if you wish
        return best_answer
    else:
        return None, None, "Sorry, I couldn't find a relevant answer to your question. Please try rephrasing or " \
                           "asking another question. "
