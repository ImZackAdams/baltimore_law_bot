from app.utils.pdf_processing import extract_text_from_pdf, clean_text

# Path to your PDF file
pdf_path = "legaldocs/Article-13-housing.pdf"

# Extract and clean the text from the PDF
main_law_text = clean_text(extract_text_from_pdf(pdf_path))