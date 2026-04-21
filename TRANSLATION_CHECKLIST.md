# Translation Checklist (SDG Assessment)

This file summarizes the current status of translations. 

## Missing / Needs Action

| Key | English | Portuguese (PT-BR) | French (FR) |
|-----|---------|-------------------|-------------|
| **Global** | | | |
| `complete_button` | *Missing* | Concluir Avaliação | *OK* |
| **SDG 1** | | | |
| `sdg1_title` | OK | *Missing* | OK |
| ... | ... | ... | ... |
| **SDG 16 (MIXED)** | | | |
| `sdg16_summary_instruction` | *Missing* | Selecione a resposta... | *OK* |
| `sdg16_comments_label` | *Missing* | COMENTÁRIO: ... | *OK* |
| **SDG 17 (MIXED)** | | | |
| `sdg17_title` | *Missing* | ODS 17: PARCERIAS... | OK |

## How to fix:
1. Update `translations_master.json` with the correct strings.
2. Run `python scripts/generate_i18n.py`.

*Note: This is a summary. See `translations_master.json` for all 574 keys.*
