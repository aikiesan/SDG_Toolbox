import re
import os

def inject_translate_keys():
    path = 'app/templates/questionnaire/assessment.html'
    if not os.path.exists(path):
        print(f"Error: {path} not found")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Section Titles
    # We find the section number by looking at the nearest data-section attribute
    def replace_section(match):
        text_before = match.string[:match.start()]
        section_matches = re.findall(r'data-section="(\d+)"', text_before)
        section_num = section_matches[-1] if section_matches else "1"
        return f'<h3 class="section-title" data-translate-key="section{section_num}_title">{match.group(1)}</h3>'

    content = re.sub(r'<h3 class="section-title">([^<]+)</h3>', replace_section, content)
    
    # 2. Update Question Text
    content = re.sub(r'<p class="question-text" id="q(\d+)-text">', 
                     r'<p class="question-text" id="q\1-text" data-translate-key="q\1_text">', 
                     content)

    # 3. Update Options
    content = re.sub(r'<label for="q(\d+)-opt(\d+)">', 
                     r'<label for="q\1-opt\2" data-translate-key="q\1_opt\2">', 
                     content)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully injected translation keys into {path}")

if __name__ == "__main__":
    inject_translate_keys()
