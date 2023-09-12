from flask import Flask
from .views import views
from app.utils.pdf_processing import extract_text_from_pdf, clean_text

# Initialize the Flask app
app = Flask(__name__)

# Path to your PDF file
pdf_path = "legaldocs/Article-13-housing.pdf"

# Extract and clean the text from the PDF
#main_law_text = clean_text(extract_text_from_pdf(pdf_path))
main_law_text = extract_text_from_pdf(pdf_path)

# Now, main_law_text contains the cleaned law text from your PDF

# Register the blueprint
app.register_blueprint(views)
