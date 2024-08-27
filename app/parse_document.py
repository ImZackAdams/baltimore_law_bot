import re
import json
import subprocess

def convert_pdf_to_txt(pdf_path, txt_path):
    subprocess.run(['pdftotext', pdf_path, txt_path], check=True)
    print(f"Converted PDF to text file: {txt_path}")

def load_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'(?<=\w)-\s+(?=\w)', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def parse_document(text):
    document_structure = {}
    unmatched_lines = []

    # Initialize variables
    current_division = None
    current_subtitle = None
    current_section = None
    current_subsection = None

    # Regular expressions to match different parts of the document
    division_pattern = re.compile(r'DIVISION\s+([IVXLCDM]+):\s+(.+)', re.IGNORECASE)
    subtitle_pattern = re.compile(r'SUBTITLE\s+(\d+)([A-Z]*)\s*(.*)', re.IGNORECASE)
    section_pattern = re.compile(r'§\s*(\d+-\d+)\.\s*(.+)', re.IGNORECASE)
    subsection_pattern = re.compile(r'^\((\w+)\)\s*(.*)', re.IGNORECASE)
    list_item_pattern = re.compile(r'^\((\d+)\)\s*(.+)', re.IGNORECASE)
    reserved_pattern = re.compile(r'\{RESERVED\}', re.IGNORECASE)
    note_pattern = re.compile(r'NOTE:\s*(.+)', re.IGNORECASE)
    ordinance_pattern = re.compile(r'\(Ord\.\s*(\d+-\d+);\s*(.+?)\)', re.IGNORECASE)
    title_pattern = re.compile(r'(ARTICLE\s+\d+\s+HOUSING\s+AND\s+URBAN\s+RENEWAL\s*\(.*?\))', re.IGNORECASE)
    heading_pattern = re.compile(r'(TABLE OF SUBTITLES|TABLE OF SECTIONS|DEFINITIONS)', re.IGNORECASE)
    subsection_alt_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)', re.IGNORECASE)

    lines = text.split('. ')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if division_pattern.match(line):
            current_division = division_pattern.match(line).group(2).strip()
            document_structure[current_division] = {}
            current_subtitle, current_section, current_subsection = None, None, None
            print(f"Found Division: {current_division}")
        elif subtitle_pattern.match(line):
            current_subtitle = subtitle_pattern.match(line).group(3).strip() or f"Subtitle {subtitle_pattern.match(line).group(1)}{subtitle_pattern.match(line).group(2)}"
            if current_division:
                document_structure[current_division][current_subtitle] = {}
                current_section, current_subsection = None, None
                print(f"  Found Subtitle: {current_subtitle} under Division: {current_division}")
        elif section_pattern.match(line):
            current_section = section_pattern.match(line).group(2).strip()
            if current_division and current_subtitle:
                document_structure[current_division][current_subtitle][current_section] = {}
                current_subsection = None
                print(f"    Found Section: {current_section} under Subtitle: {current_subtitle}")
        elif subsection_pattern.match(line):
            current_subsection = subsection_pattern.match(line).group(2).strip()
            if current_division and current_subtitle and current_section:
                document_structure[current_division][current_subtitle][current_section][current_subsection] = ""
                print(f"      Found Subsection: ({subsection_pattern.match(line).group(1)}) {current_subsection} under Section: {current_section}")
        elif list_item_pattern.match(line):
            list_item = list_item_pattern.match(line).group(2).strip()
            if current_division and current_subtitle and current_section and current_subsection:
                document_structure[current_division][current_subtitle][current_section][current_subsection] += list_item + " "
                print(f"        Adding List Item to Subsection: {current_subsection}")
        elif reserved_pattern.search(line):
            if current_division and current_subtitle and current_section:
                document_structure[current_division][current_subtitle][current_section] = "Reserved"
                print(f"      Found Reserved Section in: {current_section}")
        elif note_pattern.match(line):
            note = note_pattern.match(line).group(1).strip()
            if current_division and current_subtitle:
                document_structure[current_division][current_subtitle]["Note"] = note
                print(f"      Found Note: {note}")
        elif ordinance_pattern.match(line):
            ordinance_number = ordinance_pattern.match(line).group(1).strip()
            ordinance_details = ordinance_pattern.match(line).group(2).strip()
            if current_division and current_subtitle:
                document_structure[current_division][current_subtitle]["Ordinance"] = f"{ordinance_number}: {ordinance_details}"
                print(f"      Found Ordinance: {ordinance_number} - {ordinance_details}")
        elif title_pattern.match(line):
            title = title_pattern.match(line).group(1).strip()
            unmatched_lines.append(f"Title: {title}")
            print(f"Title identified: {title}")
        elif heading_pattern.match(line):
            heading = heading_pattern.match(line).group(1).strip()
            unmatched_lines.append(f"Heading: {heading}")
            print(f"Heading identified: {heading}")
        elif subsection_alt_pattern.match(line):
            subsection_id = subsection_alt_pattern.match(line).group(1).strip()
            subsection_text = subsection_alt_pattern.match(line).group(2).strip()
            if current_division and current_subtitle and current_section:
                document_structure[current_division][current_subtitle][current_section][subsection_id] = subsection_text
                print(f"      Found Alternate Subsection: {subsection_id} - {subsection_text}")
        else:
            unmatched_lines.append(line)
            print(f"Line not matched, added to Unmatched: {line}")

    document_structure["Unmatched"] = unmatched_lines
    return document_structure

def save_as_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print(f"Document parsed and saved successfully as {file_path}")

def main():
    pdf_path = 'article-13-housing.pdf'
    txt_path = 'article-13-housing.txt'
    json_output_path = 'document_structure.json'

    convert_pdf_to_txt(pdf_path, txt_path)

    document_text = load_text_file(txt_path)

    cleaned_text = clean_text(document_text)

    print("Cleaned Text Sample:")
    print(cleaned_text[:5000])

    document_structure = parse_document(cleaned_text)

    save_as_json(document_structure, json_output_path)

if __name__ == "__main__":
    main()
