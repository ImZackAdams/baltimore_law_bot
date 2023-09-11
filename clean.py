import PyPDF2
import re


def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a given PDF file path.
    Args:
    - pdf_path (str): The path to the PDF file.

    Returns:
    - str: Extracted text.
    """
    text = ''
    with open(pdf_path, 'rb') as file:
        pdf = PyPDF2.PdfReader(file)
        for page in pdf.pages:
            text += page.extract_text()
    return text


def clean_text(text):
    """
    Cleans the text by removing publication details and other unwanted elements.
    Args:
    - text (str): The text to clean.

    Returns:
    - str: Cleaned text.
    """
    remove_list = [
        "Published by", "BALTIMORE CITY DEPARTMENT OF LEGISLATIVE REFERENCE",
        "Avery Aisenstark, Director", "Copyright © 2022",
        "The Mayor and City Council of Baltimore", "Department of Legislative Reference",
        "All rights reserved", "For information –  call, write, or fax:",
        "626 City Hall", "Baltimore, Maryland 21202", "Tel: (410) 396-4730  F  Fax: (410) 396-8483"
    ]

    for item in remove_list:
        text = text.replace(item, '')

    return text.strip()


def extract_divisions_and_subtitles(main_content):
    """
    Extracts divisions and subtitles from the cleaned content.
    Args:
    - main_content (str): Cleaned text to extract data from.

    Returns:
    - dict: Divisions and their respective subtitles.
    """
    division_data = {}
    main_divisions = re.split(r'DIVISION [I,V,X,L,C,D,M]+\.', main_content)[1:]

    for division in main_divisions:
        division_parts = division.split("\n", 1)
        if len(division_parts) > 1:
            division_title = f"DIVISION {re.search(r'[I,V,X,L,C,D,M]+', division_parts[0]).group()}. {division_parts[0].replace(re.search(r'[I,V,X,L,C,D,M]+', division_parts[0]).group(), '').strip()}"
            subtitles = [subtitle.strip() for subtitle in re.split(r'\bSubtitle\b', division_parts[1])][1:]
            division_data[division_title] = subtitles

    return division_data


# Extract and clean content from the PDF
pdf_content = extract_text_from_pdf('legaldocs/Article-13-housing.pdf')
cleaned_content = clean_text(pdf_content)

# Extract divisions and subtitles
divisions_subtitles_data = extract_divisions_and_subtitles(cleaned_content)

# Print extracted data for verification
for division_title, subtitles in divisions_subtitles_data.items():
    print(f"\nDivision: {division_title}")
    for subtitle in subtitles:
        print(f"Subtitle: {subtitle[:100]}...")  # Printing first 100 characters for brevity
