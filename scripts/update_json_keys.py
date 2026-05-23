import json
import re
import os

def update_translations_with_standard_keys():
    template_path = 'app/templates/questionnaire/assessment.html'
    json_path = 'translations_master.json'

    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found")
        return

    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all data-translate-key="key"
    keys = re.findall(r'data-translate-key="([^"]+)"', content)
    
    # Also find all id="qX-text" and id="qX-optY" which should be translated
    # Actually, we should use the keys we ALREADY added to the template if I did that.
    # Let me check if I already added them.
    
    # Wait, I didn't finish adding the keys to the template because I was interrupted.
    # I should add the keys to the template FIRST, then extract them.
    # Or I can just manually define the keys for the 31 questions.

    q_keys = []
    for i in range(1, 32):
        q_keys.append(f"q{i}_text")
        q_keys.append(f"q{i}_help")
        for j in range(1, 7): # Assuming max 6 options
            q_keys.append(f"q{i}_opt{j}")

    all_standard_keys = [
        "standard_assessment_title",
        "standard_assessment_subtitle",
        "progression_label",
        "project_info_step",
        "assessment_step",
        "section1_title", "section2_title", "section3_title", "section4_title", "section5_title", "section6_title", "section7_title",
        "continue_button", "back_button", "complete_button"
    ] + q_keys

    with open(json_path, 'r', encoding='utf-8') as f:
        master = json.load(f)

    added = 0
    for key in all_standard_keys:
        if key not in master:
            master[key] = {"en": "", "fr": "", "pt-br": ""}
            added += 1

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(master, f, indent=2, ensure_ascii=False)

    print(f"Successfully added {added} new keys to translations_master.json")

if __name__ == "__main__":
    update_translations_with_standard_keys()
