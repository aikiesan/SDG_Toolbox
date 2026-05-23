import json
import re
import os

def extract_en():
    path = 'app/templates/questionnaire/assessment.html'
    if not os.path.exists(path):
        print(f"Error: {path} not found")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    data = {}

    # 1. Headers
    title = re.search(r'data-translate-key="standard_assessment_title"[^>]*>([^<]+)</h1>', content)
    if title: data["standard_assessment_title"] = {"en": title.group(1).strip(), "fr": "", "pt-br": ""}

    subtitle = re.search(r'data-translate-key="standard_assessment_subtitle"[^>]*>([^<]+)</p>', content)
    if subtitle: data["standard_assessment_subtitle"] = {"en": subtitle.group(1).strip(), "fr": "", "pt-br": ""}

    # 2. Sections
    sections = re.findall(r'data-translate-key="(section\d+_title)"[^>]*>([^<]+)</h3>', content)
    for key, text in sections:
        data[key] = {"en": text.strip(), "fr": "", "pt-br": ""}

    # 3. Questions
    questions = re.findall(r'data-translate-key="(q\d+_text)"[^>]*>([^<]+)</p>', content)
    for key, text in questions:
        data[key] = {"en": text.strip(), "fr": "", "pt-br": ""}

    # 4. Options
    options = re.findall(r'data-translate-key="(q\d+_opt\d+)"[^>]*>([^<]+)</label>', content)
    for key, text in options:
        data[key] = {"en": text.strip(), "fr": "", "pt-br": ""}

    with open('translations_standard.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully extracted {len(data)} strings to translations_standard.json")

if __name__ == "__main__":
    extract_en()
