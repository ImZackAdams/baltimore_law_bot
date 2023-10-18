import PyPDF2
import re
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


# Now, ROOT_DIR contains the path "/Users/zack/Desktop/baltimore-law-bot/"

def extract_text_from_pdf(pdf_path='legaldocs/Article-13-housing.pdf'):
    # Update the pdf_path to be relative to the ROOT_DIR
    pdf_path = os.path.join(ROOT_DIR, pdf_path)
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
        "626 City Hall", "Baltimore, Maryland 21202", "Tel: (410) 396-4730  F  Fax: (410) 396-8483",
        "TABLE OF SUBTITLES", "ARTICLE 13", "HOUSING AND URBAN RENEWAL", "(As Last Amended by Ords. 22-124 and 22-125)"
    ]

    for item in remove_list:
        text = text.replace(item, '')
    text = text.replace("D\nIVISION", "DIVISION")
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()


def extract_sections_titles_subtitles(text):
    sections = []
    current_title = ""
    current_subtitle = ""
    current_content = ""

    title_marker = "DIVISION"
    subtitle_marker = "SUBTITLE"

    for line in text.split('\n'):
        if title_marker in line:
            if current_content or current_subtitle:
                sections.append({
                    'title': current_title,
                    'subtitle': current_subtitle,
                    'content': current_content.strip(),
                })

            current_title = line.strip()
            current_subtitle = ""
            current_content = ""
        elif subtitle_marker in line:
            if current_subtitle:  # Save the previous subtitle before starting a new one
                sections.append({
                    'title': current_title,
                    'subtitle': current_subtitle,
                    'content': current_content.strip(),
                })
                current_content = ""  # Reset content for the new subtitle
            current_subtitle = line.strip()
        else:
            current_content += line + '\n'

    if current_content or current_subtitle:
        sections.append({
            'title': current_title,
            'subtitle': current_subtitle,
            'content': current_content.strip(),
        })

    return sections


def search_sections(query, sections):
    for section in sections:
        if query.lower() in section['content'].lower():
            return section['content']
    return None


# Extract text from the PDF
pdf_content = extract_text_from_pdf('legaldocs/Article-13-housing.pdf')
print("\n===== First 500 characters of the PDF content =====")
print(pdf_content[:500])  # print the first 500 characters

# Clean the text
cleaned_content = clean_text(pdf_content)
print("\n===== First 500 characters of the cleaned content =====")
print(cleaned_content[:500])  # print the first 500 characters after cleaning

# Extract sections based on divisions and subtitles
sections = extract_sections_titles_subtitles(cleaned_content)
print("\n===== First 3 sections =====")
for section in sections[:3]:  # print details of the first 3 sections
    print("\nTitle:", section['title'])
    print("Subtitle:", section['subtitle'])
    print("Content (first 200 characters):", section['content'][:200], "...\n")

test_query = "housing"  # or another known keyword
result = search_sections(test_query, sections)
print(result[:500]) if result else print("No match found.")
