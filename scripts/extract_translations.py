#!/usr/bin/env python3
import json
import re
import os

def extract_translations():
    js_path = 'app/static/js/assessment/i18n_assessment.js'
    if not os.path.exists(js_path):
        print(f"Error: {js_path} not found")
        return

    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find the blocks: en: { ... }, fr: { ... }
    # Use a greedy match for the content between curly braces, but try to find the end of the block
    en_match = re.search(r'en:\s*\{(.*?)\n\s*\},', content, re.DOTALL)
    fr_match = re.search(r'fr:\s*\{(.*?)\n\s*\}', content, re.DOTALL)

    def parse_block(block_text):
        if not block_text:
            return {}
        # Match key: `value` (handles backticks, single, and double quotes)
        # We use a non-greedy .*? for the value but be careful with escaped quotes
        # This is a bit simplified but should work for this specific file structure
        pattern = r'(\w+):\s*[`\'\"](.*?)[`\'\"],'
        matches = re.findall(pattern, block_text, re.DOTALL)
        return {k: v.strip() for k, v in matches}

    en_raw = parse_block(en_match.group(1) if en_match else "")
    fr_raw = parse_block(fr_match.group(1) if fr_match else "")

    master = {}
    all_keys = sorted(set(list(en_raw.keys()) + list(fr_raw.keys())))

    # Heuristic for Portuguese words to catch the "bleed"
    pt_keywords = ['para', 'com', 'ção', 'mentação', 'pobreza', 'fome', 'saúde', 'educação', 'igualdade', 'água', 'energia', 'trabalho', 'indústria', 'redução', 'cidades', 'consumo', 'ação', 'vida', 'paz', 'parcerias']

    for k in all_keys:
        en_val = en_raw.get(k, '')
        fr_val = fr_raw.get(k, '')
        pt_val = ""

        # Move Portuguese text from EN block to PT-BR if it looks like Portuguese
        is_pt = any(word in en_val.lower() for word in pt_keywords) and ('sdg16' in k or 'sdg17' in k or 'complete' in k)
        
        if is_pt:
            pt_val = en_val
            en_val = "" # Needs English translation

        master[k] = {
            "en": en_val,
            "fr": fr_val,
            "pt-br": pt_val
        }

    with open('translations_master.json', 'w', encoding='utf-8') as f:
        json.dump(master, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully extracted {len(master)} keys to translations_master.json")

if __name__ == "__main__":
    extract_translations()
