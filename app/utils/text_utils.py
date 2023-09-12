import re
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


def extract_content_from_section(section_title, main_content):
    if section_title not in main_content:
        print(f"Warning: {section_title} not found in main content!")
        return ""

    start_idx = main_content.index(section_title)
    end_idx = main_content.find("DIVISION", start_idx + 1)

    if end_idx == -1:
        end_idx = len(main_content)

    return main_content[start_idx:end_idx]


def is_unsatisfactory(answer):
    if "division" in answer.lower() or "subtitle" in answer.lower():
        return True
    return False


def retrieve_top_n_sections(query, embeddings, n=3):
    query_embedding = model.encode(query, convert_to_tensor=True)
    similarities = []
    for text, embed in embeddings.items():
        sim = util.pytorch_cos_sim(query_embedding, embed)
        similarities.append((text, float(sim)))
    sorted_sections = sorted(similarities, key=lambda x: x[1], reverse=True)
    return [section[0] for section in sorted_sections[:n]]


def extract_divisions_and_subtitles(main_content):
    division_data = {}

    # Find all divisions in the content
    division_matches = re.findall(r'DIVISION [IVXLCDM]+', main_content)

    # Refining the subtitle pattern
    subtitle_pattern = re.compile(r'Subtitle (\d+[A-Z]*\.)\s*([^S]{10,}?)(?=Subtitle|DIVISION|\Z)', re.DOTALL)

    for i in range(len(division_matches)):
        start_idx = main_content.index(division_matches[i])
        if i + 1 < len(division_matches):
            end_idx = main_content.index(division_matches[i + 1])
        else:
            end_idx = len(main_content)

        content = main_content[start_idx:end_idx]
        subtitles = subtitle_pattern.findall(content)

        cleaned_subtitles = []
        for num, desc in subtitles:
            cleaned_desc = desc.split("DIVISION", 1)[0]  # Split by next "DIVISION" if present
            subtitle = "{} {}".format(num.strip('.'), cleaned_desc.replace('\n', ' ').strip())
            if not subtitle.endswith("{Reserved}") and not subtitle.endswith("{Vacant}"):  # Skip placeholder subtitles
                cleaned_subtitles.append(subtitle)

        division_data[division_matches[i]] = cleaned_subtitles

    return division_data


def retrieve_most_relevant(query, embeddings):
    query_embedding = model.encode(query, convert_to_tensor=True)
    max_sim = -1
    most_relevant = ""

    for text, embed in embeddings.items():
        sim = util.pytorch_cos_sim(query_embedding, embed)
        if sim > max_sim:
            max_sim = sim
            most_relevant = text

    if max_sim < 0.6:
        return "No relevant section found."

    return most_relevant


def reformulate_query(query):
    stopwords = ["does", "is", "are", "me", "my", "a", "?"]
    words = query.lower().split()
    cleaned_words = [word for word in words if word not in stopwords]

    # Optionally add more sophisticated reformulation techniques here

    return ' '.join(cleaned_words)
