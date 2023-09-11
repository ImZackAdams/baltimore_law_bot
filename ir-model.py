from sentence_transformers import SentenceTransformer, util
import numpy as np

# Initialize SBERT model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


def create_embeddings(data):
    """
    Create embeddings for each division and subtitle.
    Args:
    - data (dict): Divisions and their respective subtitles.

    Returns:
    - dict: Embeddings for divisions and subtitles.
    """
    embeddings = {}
    for division, subtitles in data.items():
        embeddings[division] = model.encode(division)
        for subtitle in subtitles:
            key = f"{division} - {subtitle[:100]}"  # Unique key with division and start of subtitle
            embeddings[key] = model.encode(subtitle)
    return embeddings


# Create embeddings for extracted data
embeddings_data = create_embeddings(divisions_subtitles_data)


def retrieve_most_relevant(query, embeddings):
    """
    Retrieves the most relevant passage based on user's query.
    Args:
    - query (str): User's question.
    - embeddings (dict): Embeddings for divisions and subtitles.

    Returns:
    - str: Most relevant passage.
    """
    query_embedding = model.encode(query, convert_to_tensor=True)
    max_sim = -1
    most_relevant = ""

    for text, embed in embeddings.items():
        sim = util.pytorch_cos_sim(query_embedding, embed)
        if sim > max_sim:
            max_sim = sim
            most_relevant = text
    return most_relevant


# Testing the retrieval function
query = input("Ask a legal question related to housing: ")
response = retrieve_most_relevant(query, embeddings_data)
print(f"Most relevant section: {response}")
