import re
import json
import subprocess

def convert_pdf_to_txt(pdf_path, txt_path):
    """
    Convert PDF to text using pdftotext command-line utility.
    """
    subprocess.run(['pdftotext', pdf_path, txt_path], check=True)
    print(f"Converted PDF to text file: {txt_path}")

def load_text_file(file_path):
    """
    Load text from a text file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def clean_text(text):
    """
    Clean the extracted text to remove artifacts.
    """
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces/newlines with a single space
    text = re.sub(r'(?<=\w)-\s+(?=\w)', '', text)  # Fix word breaks caused by hyphenation
    text = re.sub(r'\s{2,}', ' ', text)  # Remove any remaining multiple spaces
    return text.strip()

def parse_document(text):
    """
    Parse the cleaned document into a structured format.
    """
    document_structure = {}
    current_division = None
    current_subtitle = None
    current_section = None
    current_subsection = None

    # Regular expressions to match divisions, subtitles, sections, subsections, etc.
    division_pattern = re.compile(r'DIVISION\s+([IVXLCDM]+):\s+(.+)', re.IGNORECASE)
    subtitle_pattern = re.compile(r'SUBTITLE\s+(\d+)\s*(.*)')
    section_pattern = re.compile(r'§\s*(\d+-\d+)\.\s*(.+)')
    subsection_pattern = re.compile(r'^\((\w+)\)\s*(.*)')
    list_item_pattern = re.compile(r'^\((\d+)\)\s*(.+)')
    reserved_pattern = re.compile(r'\{RESERVED\}')
    note_pattern = re.compile(r'NOTE:\s*(.+)')
    ordinance_pattern = re.compile(r'\(Ord\.\s*(\d+-\d+);\s*(.+?)\)')

    lines = text.split('. ')
    for line in lines:
        line = line.strip()  # Strip leading and trailing spaces
        division_match = division_pattern.match(line)
        subtitle_match = subtitle_pattern.match(line)
        section_match = section_pattern.match(line)
        subsection_match = subsection_pattern.match(line)
        list_item_match = list_item_pattern.match(line)
        reserved_match = reserved_pattern.search(line)
        note_match = note_pattern.match(line)
        ordinance_match = ordinance_pattern.match(line)

        if division_match:
            current_division = division_match.group(2)
            document_structure[current_division] = {}
            print(f"Found Division: {current_division}")
        elif subtitle_match:
            current_subtitle = subtitle_match.group(2) or f"Subtitle {subtitle_match.group(1)}"
            if current_division:
                document_structure[current_division][current_subtitle] = {}
                print(f"  Found Subtitle: {current_subtitle} under Division: {current_division}")
        elif section_match:
            current_section = section_match.group(2)
            if current_division and current_subtitle:
                document_structure[current_division][current_subtitle][current_section] = {}
                print(f"    Found Section: {current_section} under Subtitle: {current_subtitle}")
        elif subsection_match:
            current_subsection = subsection_match.group(2)
            if current_division and current_subtitle and current_section:
                document_structure[current_division][current_subtitle][current_section][current_subsection] = ""
                print(f"      Found Subsection: ({subsection_match.group(1)}) {current_subsection} under Section: {current_section}")
        elif list_item_match:
            list_item = list_item_match.group(2)
            if current_division and current_subtitle and current_section and current_subsection:
                document_structure[current_division][current_subtitle][current_section][current_subsection] += list_item + " "
                print(f"        Adding List Item to Subsection: {current_subsection}")
        elif reserved_match:
            if current_division and current_subtitle and current_section:
                document_structure[current_division][current_subtitle][current_section] = "Reserved"
                print(f"      Found Reserved Section in: {current_section}")
        elif note_match:
            note = note_match.group(1)
            if current_division and current_subtitle:
                document_structure[current_division][current_subtitle]["Note"] = note
                print(f"      Found Note: {note}")
        elif ordinance_match:
            ordinance_number = ordinance_match.group(1)
            ordinance_details = ordinance_match.group(2)
            if current_division and current_subtitle:
                document_structure[current_division][current_subtitle]["Ordinance"] = f"{ordinance_number}: {ordinance_details}"
                print(f"      Found Ordinance: {ordinance_number} - {ordinance_details}")
        elif current_division and current_subtitle and current_section and current_subsection:
            document_structure[current_division][current_subtitle][current_section][current_subsection] += line + " "
            print(f"        Adding content to Subsection: {current_subsection}")
        elif current_division and current_subtitle and current_section:
            document_structure[current_division][current_subtitle][current_section] += line + " "
            print(f"      Adding content to Section: {current_section}")
        else:
            # Fallback mechanism to handle unmatched lines
            unmatched_section = document_structure.setdefault("Unmatched", [])
            unmatched_section.append(line)
            print(f"Line not matched, added to Unmatched: {line}")

    return document_structure

def save_as_json(data, file_path):
    """
    Save the structured data as a JSON file.
    """
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print(f"Document parsed and saved successfully as {file_path}")

def main():
    pdf_path = 'article-13-housing.pdf'
    txt_path = 'article-13-housing.txt'
    json_output_path = 'document_structure.json'

    # Convert PDF to TXT
    convert_pdf_to_txt(pdf_path, txt_path)

    # Load text from the TXT file
    document_text = load_text_file(txt_path)

    # Clean the extracted text
    cleaned_text = clean_text(document_text)

    # Print the cleaned text sample for inspection
    print("Cleaned Text Sample:")
    print(cleaned_text[:5000])  # Print the first 5000 characters for inspection

    # Parse the cleaned document into a structured format
    document_structure = parse_document(cleaned_text)

    # Save the structured data as a JSON file
    save_as_json(document_structure, json_output_path)

if __name__ == "__main__":
    main()
