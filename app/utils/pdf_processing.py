import PyPDF2


def extract_text_from_pdf(pdf_path='legaldocs/Article-13-housing.pdf'):
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


def extract_sections_titles_subtitles(text):
    sections = []
    current_title = ""
    current_subtitle = ""
    current_content = ""

    # You would need to adapt these to the actual markers or formatting used in your document
    title_marker = "TITLE:"
    subtitle_marker = "SUBTITLE:"

    for line in text.split('\n'):
        if title_marker in line:
            # Save the current section before starting a new one
            if current_content:
                sections.append({
                    'title': current_title,
                    'subtitle': current_subtitle,
                    'content': current_content.strip(),
                })

            # Start a new section
            current_title = line.replace(title_marker, '').strip()
            current_subtitle = ""
            current_content = ""
        elif subtitle_marker in line:
            current_subtitle = line.replace(subtitle_marker, '').strip()
        else:
            current_content += line + '\n'

    # Don't forget to save the last section
    if current_content:
        sections.append({
            'title': current_title,
            'subtitle': current_subtitle,
            'content': current_content.strip(),
        })

    return sections
