"""One-shot script: adds results-page translation keys to translations_master.json."""
import json

new_keys = {
    "perf_excellent":          {"en": "Excellent",            "pt-br": "Excelente",                          "fr": "Excellent"},
    "perf_good":               {"en": "Good",                 "pt-br": "Bom",                                "fr": "Bien"},
    "perf_fair":               {"en": "Fair",                 "pt-br": "Regular",                            "fr": "Passable"},
    "perf_needs_improvement":  {"en": "Needs Improvement",    "pt-br": "Precisa Melhorar",                   "fr": "À Améliorer"},
    "score_label":             {"en": "Score",                "pt-br": "Pontuação",                "fr": "Score"},
    "pdf_alert":               {"en": "PDF generation is not fully implemented. Printing the page is a temporary alternative.",
                                "pt-br": "A geração de PDF não está totalmente implementada. Imprimir a página é uma alternativa temporária.",
                                "fr": "La génération de PDF n'est pas entièrement implémentée. L'impression de la page est une alternative temporaire."},
    "expert_results_heading":         {"en": "Expert Assessment Report",         "pt-br": "Relatório de Avaliação Especializada",  "fr": "Rapport d'Évaluation Expert"},
    "expert_results_project_label":   {"en": "Project:",                         "pt-br": "Projeto:",                                             "fr": "Projet :"},
    "expert_results_assessed_on":     {"en": "Assessed on:",                     "pt-br": "Avaliado em:",                                         "fr": "Évalué le :"},
    "expert_results_overview_title":  {"en": "SDG Performance Overview",         "pt-br": "Visão Geral do Desempenho dos ODS",               "fr": "Aperçu des Performances ODD"},
    "expert_results_scores_title":    {"en": "Scores per SDG",                   "pt-br": "Pontuações por ODS",                         "fr": "Scores par ODD"},
    "expert_results_breakdown_title": {"en": "Detailed Performance by SDG",      "pt-br": "Desempenho Detalhado por ODS",                         "fr": "Performance Détaillée par ODD"},
    "expert_results_print_btn":       {"en": "Print Results",                    "pt-br": "Imprimir Resultados",                                  "fr": "Imprimer les Résultats"},
    "expert_results_pdf_btn":         {"en": "Download PDF",                     "pt-br": "Baixar PDF",                                           "fr": "Télécharger le PDF"},
    "expert_results_new_btn":         {"en": "Start New Expert Assessment",      "pt-br": "Iniciar Nova Avaliação Especializada",        "fr": "Démarrer une Nouvelle Évaluation Expert"},
    "results_page_title":             {"en": "SDG Assessment Results",           "pt-br": "Resultados da Avaliação dos ODS",             "fr": "Résultats de l'Évaluation ODD"},
    "results_overall_score_label":    {"en": "Overall Score",                    "pt-br": "Pontuação Geral",                            "fr": "Score Global"},
    "results_top_category_label":     {"en": "Top Performing Category",          "pt-br": "Categoria de Melhor Desempenho",                       "fr": "Catégorie la Mieux Notée"},
    "results_sdgs_evaluated_label":   {"en": "SDGs Evaluated",                   "pt-br": "ODS Avaliados",                                        "fr": "ODD Évalués"},
    "results_print_btn":              {"en": "Print",                            "pt-br": "Imprimir",                                             "fr": "Imprimer"},
    "results_share_btn":              {"en": "Share",                            "pt-br": "Compartilhar",                                         "fr": "Partager"},
    "results_save_image_btn":         {"en": "Save Image",                       "pt-br": "Salvar Imagem",                                        "fr": "Enregistrer l'Image"},
    "results_radar_title":            {"en": "SDG Radar Performance",            "pt-br": "Radar de Desempenho dos ODS",                          "fr": "Radar de Performance ODD"},
    "results_breakdown_title":        {"en": "Score Breakdown",                  "pt-br": "Detalhamento da Pontuação",                  "fr": "Détail des Scores"},
    "results_5p_title":               {"en": "Performance by Category (5 P's)",  "pt-br": "Desempenho por Categoria (5 P's)",                     "fr": "Performance par Catégorie (5 P)"},
    "results_dimensions_title":       {"en": "SDG Dimensions",                   "pt-br": "Dimensões dos ODS",                               "fr": "Dimensions des ODD"},
    "results_ranking_title":          {"en": "SDG Performance Ranking",          "pt-br": "Ranking de Desempenho dos ODS",                        "fr": "Classement des Performances ODD"},
    "results_col_name":               {"en": "Name",                             "pt-br": "Nome",                                                 "fr": "Nom"},
    "results_col_direct":             {"en": "Direct Score",                     "pt-br": "Pontuação Direta",                           "fr": "Score Direct"},
    "results_col_bonus":              {"en": "Bonus Score",                      "pt-br": "Pontuação Bônus",                       "fr": "Score Bonus"},
    "results_col_total":              {"en": "Total Score",                      "pt-br": "Pontuação Total",                            "fr": "Score Total"},
    "results_col_performance":        {"en": "Performance",                      "pt-br": "Desempenho",                                           "fr": "Performance"},
    "results_no_scores":              {"en": "No SDG scores available.",         "pt-br": "Nenhuma pontuação de ODS disponível.",   "fr": "Aucun score ODD disponible."},
    "results_recommendations_title":  {"en": "Tailored Recommendations",         "pt-br": "Recomendações Personalizadas",               "fr": "Recommandations Personnalisées"},
    "results_no_recommendations":     {"en": "Recommendations cannot be generated as no scores are available.",
                                       "pt-br": "Não é possível gerar recomendações pois não há pontuações disponíveis.",
                                       "fr": "Les recommandations ne peuvent pas être générées car aucun score n'est disponible."},
    "results_learn_more_title":       {"en": "Learn More & Improve Your Project","pt-br": "Saiba Mais e Melhore seu Projeto",                     "fr": "En Savoir Plus et Améliorer votre Projet"},
    "results_share_title":            {"en": "Share Assessment Results",         "pt-br": "Compartilhar Resultados da Avaliação",       "fr": "Partager les Résultats de l'Évaluation"},
    "results_share_desc":             {"en": "Share this assessment with others using the link below. The link will expire in 30 days.",
                                       "pt-br": "Compartilhe esta avaliação com outras pessoas usando o link abaixo. O link expirará em 30 dias.",
                                       "fr": "Partagez cette évaluation avec d'autres personnes via le lien ci-dessous. Le lien expirera dans 30 jours."},
    "results_share_link_label":       {"en": "Shareable Link",                   "pt-br": "Link para Compartilhamento",                           "fr": "Lien de Partage"},
    "results_copy_link_btn":          {"en": "Copy Link",                        "pt-br": "Copiar Link",                                          "fr": "Copier le Lien"},
    "results_share_readonly":         {"en": "Anyone with this link can view the results (read-only)",
                                       "pt-br": "Qualquer pessoa com este link pode visualizar os resultados (somente leitura)",
                                       "fr": "Toute personne disposant de ce lien peut consulter les résultats (lecture seule)"},
    "results_close_btn":              {"en": "Close",                            "pt-br": "Fechar",                                               "fr": "Fermer"},
    "results_chart_view":             {"en": "Chart View",                       "pt-br": "Visualização em Gráfico",              "fr": "Vue Graphique"},
    "results_download_chart":         {"en": "Download Chart",                   "pt-br": "Baixar Gráfico",                                  "fr": "Télécharger le Graphique"},
    "results_export_btn":             {"en": "Export All Data",                  "pt-br": "Exportar Todos os Dados",                              "fr": "Exporter Toutes les Données"},
}

with open("translations_master.json", encoding="utf-8") as f:
    master = json.load(f)

master.update(new_keys)

with open("translations_master.json", "w", encoding="utf-8") as f:
    json.dump(master, f, ensure_ascii=False, indent=2)

print(f"Done. Master now has {len(master)} keys. Added {len(new_keys)} new keys.")
