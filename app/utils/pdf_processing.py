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
