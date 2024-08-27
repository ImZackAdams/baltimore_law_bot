import json

# Load the JSON structure
with open('document_structure.json', 'r', encoding='utf-8') as json_file:
    document_structure = json.load(json_file)

# Print a sample from the JSON file
for division, subtitles in document_structure.items():
    print(f"Division: {division}")
    for subtitle, sections in subtitles.items():
        print(f"  Subtitle: {subtitle}")
        for section, content in sections.items():
            print(f"    Section: {section} -> Content starts with: {content[:60]}...")
    break  # Only print the first division and subtitle for brevity
