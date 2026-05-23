import re
import os

def final_template_injection():
    path = 'app/templates/questionnaire/assessment.html'
    if not os.path.exists(path):
        print(f"Error: {path} not found")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Navigation buttons
    content = content.replace('<span class="radio-indicator"><i class="fas fa-dot-circle"></i> Select one option only</span>', 
                              '<span class="radio-indicator" data-translate-key="select_one_option"><i class="fas fa-dot-circle"></i> Select one option only</span>')
    
    content = content.replace('<span class="checkbox-indicator"><i class="fas fa-check-square"></i> Select all that apply</span>', 
                              '<span class="checkbox-indicator" data-translate-key="select_all_options"><i class="fas fa-check-square"></i> Select all that apply</span>')

    content = content.replace('Save Progress', '<span data-translate-key="save_progress_button">Save Progress</span>')

    # 2. Tooltips
    # We find tooltips by their question context
    def replace_tooltip(match):
        q_num = match.group(1)
        tooltip_text = match.group(2)
        key = f"q{q_num}_help"
        return f'<span class="tooltip-text" data-translate-key="{key}">{tooltip_text}</span>'

    # Regex to find tooltips inside question-header
    # Looking for <p ... id="q1-text"> ... <span class="tooltip-text">TEXT</span>
    # This is a bit approximate but should work for your structure
    content = re.sub(r'id="q(\d+)-text".*?<span class="tooltip-text">([^<]+)</span>', replace_tooltip, content, flags=re.DOTALL)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Final injection complete for {path}")

if __name__ == "__main__":
    final_template_injection()
