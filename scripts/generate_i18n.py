#!/usr/bin/env python3
import json
import os

def generate_js():
    master_path = 'translations_master.json'
    js_path = 'app/static/js/assessment/i18n_assessment.js'
    
    if not os.path.exists(master_path):
        print(f"Error: {master_path} not found")
        return

    with open(master_path, 'r', encoding='utf-8') as f:
        master = json.load(f)

    # Rebuild the JS content
    output = []
    output.append("// js/assessment/i18n_assessment.js")
    output.append("// Internationalization: EN / PT-BR / FR  —  auto-generated, do not edit manually")
    output.append("")
    output.append("let currentLanguage = 'en';")
    output.append("")
    output.append("const translations = {")

    langs = ['en', 'pt-br', 'fr']
    
    for lang in langs:
        output.append(f"    '{lang}': {{")
        # Sort keys to keep file consistent
        for key in sorted(master.keys()):
            val = master[key].get(lang, "")
            # Use backticks for values to handle multi-line strings
            val = val.replace('`', '\\`')
            output.append(f"        {key}: `{val}`,")
        output.append("    },")
    
    output.append("};")
    output.append("")
    output.append("// Global availability")
    output.append("window.translations = translations;")
    output.append("window.currentLanguage = currentLanguage;")
    output.append("")
    output.append("// Function to set language and update UI")
    output.append("function setLanguage(lang) {")
    output.append("    // Bulletproof mapping for Portuguese variants")
    output.append("    if (lang === 'pt') lang = 'pt-br';")
    output.append("    ")
    output.append("    if (!translations[lang]) { ")
    output.append("        console.warn('Language ' + lang + ' not supported, falling back to English');")
    output.append("        lang = 'en';")
    output.append("    }")
    output.append("    ")
    output.append("    currentLanguage = lang;")
    output.append("    window.currentLanguage = lang; // Ensure global sync for charting")
    output.append("    ")
    output.append("    // Update button states in switcher")
    output.append("    document.querySelectorAll('.lang-btn').forEach(btn => {")
    output.append("        const btnLang = btn.getAttribute('data-lang');")
    output.append("        if (btnLang === lang || (lang === 'pt-br' && btnLang === 'pt')) {")
    output.append("            btn.classList.add('lang-btn-active');")
    output.append("        } else {")
    output.append("            btn.classList.remove('lang-btn-active');")
    output.append("        }")
    output.append("    });")
    output.append("")
    output.append("    // Trigger UI update if function exists (provided by ui_assessment.js)")
    output.append("    if (typeof updateUIForLanguage === 'function') {")
    output.append("        updateUIForLanguage();")
    output.append("    }")
    output.append("    ")
    output.append("    // Store preference using consistent key used by main_assessment.js")
    output.append("    localStorage.setItem('sdgAssessmentLang', lang);")
    output.append("}")
    output.append("")
    output.append("// Load preference on start")
    output.append("document.addEventListener('DOMContentLoaded', () => {")
    output.append("    // ALWAYS check localStorage first, but default to English if empty")
    output.append("    const savedLang = localStorage.getItem('sdgAssessmentLang');")
    output.append("    if (savedLang && (translations[savedLang] || savedLang === 'pt')) {")
    output.append("        setLanguage(savedLang);")
    output.append("    } else {")
    output.append("        // Default is English, ignore browser settings")
    output.append("        setLanguage('en');")
    output.append("    }")
    output.append("});")
    output.append("")
    output.append("if (typeof module !== 'undefined' && module.exports) module.exports = translations;")

    with open(js_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(output))
    
    print(f"Successfully generated {js_path}")

if __name__ == "__main__":
    generate_js()
