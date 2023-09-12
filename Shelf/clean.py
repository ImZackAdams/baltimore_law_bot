import torch
from transformers import BertForQuestionAnswering, BertTokenizer
import PyPDF2
import re
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

qa_model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')


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


def answer_question(question, context):
    input_ids = tokenizer.encode(question, context, return_tensors='pt')
    outputs = qa_model(input_ids)

    start_scores = outputs.start_logits
    end_scores = outputs.end_logits

    if not isinstance(start_scores, torch.Tensor) or not isinstance(end_scores, torch.Tensor):
        raise ValueError("Expected tensors but received different types.")

    all_tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
    answer = ' '.join(all_tokens[torch.argmax(start_scores): torch.argmax(end_scores) + 1])
    answer = answer.replace(' ##', '').strip()

    if "division" in answer.lower():
        answer = answer.split("division", 1)[1].strip()

    return answer


def retrieve_top_n_sections(query, embeddings, n=3):
    query_embedding = model.encode(query, convert_to_tensor=True)
    similarities = []
    for text, embed in embeddings.items():
        sim = util.pytorch_cos_sim(query_embedding, embed)
        similarities.append((text, float(sim)))
    sorted_sections = sorted(similarities, key=lambda x: x[1], reverse=True)
    return [section[0] for section in sorted_sections[:n]]


def extract_text_from_pdf(pdf_path):
    text = ''
    with open(pdf_path, 'rb') as file:
        pdf = PyPDF2.PdfReader(file)
        for page in pdf.pages:
            text += page.extract_text()
    return text


def clean_text(text):
    remove_list = [
        "Published by", "BALTIMORE CITY DEPARTMENT OF LEGISLATIVE REFERENCE",
        "Avery Aisenstark, Director", "Copyright © 2022",
        "The Mayor and City Council of Baltimore", "Department of Legislative Reference",
        "All rights reserved", "For information –  call, write, or fax:",
        "626 City Hall", "Baltimore, Maryland 21202", "Tel: (410) 396-4730  F  Fax: (410) 396-8483"
    ]

    for item in remove_list:
        text = text.replace(item, '')
    text = text.replace("D\nIVISION", "DIVISION")
    return text.strip()


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


def create_combined_embeddings(data):
    embeddings = {}
    for division, subtitles in data.items():
        for subtitle in subtitles:
            key = f"{division} - {subtitle[:100]}"
            combined_text = division + " " + subtitle
            embeddings[key] = model.encode(combined_text)
    return embeddings


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
    # Simple rule-based reformulation can be extended
    query = query.lower().replace("does", "").replace("is", "").replace("are", "").replace("?", "")
    query = query.replace("me", "").replace("my", "").replace("a", "")
    return ' '.join(query.split())


# Extract and clean content from the PDF
pdf_content = extract_text_from_pdf('../legaldocs/Article-13-housing.pdf')
cleaned_content = clean_text(pdf_content)

# Extract divisions and subtitles
divisions_subtitles_data = extract_divisions_and_subtitles(cleaned_content)

# Create embeddings for combined data
embeddings_combined_data = create_combined_embeddings(divisions_subtitles_data)

print(divisions_subtitles_data)

# User query
query = input("Enter your query: ")
reformulated_query = reformulate_query(query)

# Fetch the top-n relevant sections for the reformulated query
top_sections = retrieve_top_n_sections(reformulated_query, embeddings_combined_data, n=3)

best_answer = None
best_section = None
for section in top_sections:
    section_content = extract_content_from_section(section, cleaned_content)  # Extracting the content of the section
    answer = answer_question(query, section_content)  # Now getting the answer from that section's content
    if answer and not is_unsatisfactory(answer):
        best_answer = answer
        best_section = section
        break

if best_answer:
    print("Relevant Section:", best_section)
    print("Answer:", best_answer)
else:
    print("No relevant section found.")

section_title = "DIVISION II - 5 Licensing of Rental Dwellings"
position = cleaned_content.find(section_title)

if position != -1:
    print("Found section title. Surrounding content:")
    print(cleaned_content[max(position-50, 0):position + len(section_title) + 50])
else:
    print("Section title not found in cleaned_content.")


