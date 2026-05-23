import json
import os

def add_ui_keys():
    path = 'translations_master.json'
    with open(path, 'r', encoding='utf-8') as f:
        master = json.load(f)

    ui_keys = {
        'select_one_option': {
            'en': 'Select one option only', 
            'fr': 'Sélectionnez une seule option', 
            'pt-br': 'Selecione apenas uma opção'
        },
        'select_all_options': {
            'en': 'Select all that apply', 
            'fr': "Sélectionnez tout ce qui s'applique", 
            'pt-br': 'Selecione todas as que se aplicam'
        },
        'back_to_project': {
            'en': 'Back to Project', 
            'fr': 'Retour au Projet', 
            'pt-br': 'Voltar ao Projeto'
        },
        'save_progress_button': {
            'en': 'Save Progress', 
            'fr': 'Sauvegarder la progression', 
            'pt-br': 'Salvar Progresso'
        }
    }

    for k, v in ui_keys.items():
        master[k] = v

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(master, f, indent=2, ensure_ascii=False)
    print("Added UI keys to translations_master.json")

if __name__ == "__main__":
    add_ui_keys()
