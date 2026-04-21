"""Patches results.html: adds remaining data-translate-key attrs + i18n scripts in one pass."""
import re

path = "app/templates/questionnaire/results.html"
with open(path, encoding="utf-8") as f:
    html = f.read()

replacements = [
    # Chart titles
    ('<h4 class="chart-title">Performance by Category (5 P\'s)</h4>',
     '<h4 class="chart-title" data-translate-key="results_5p_title">Performance by Category (5 P\'s)</h4>'),
    ('<h4 class="chart-title">SDG Dimensions</h4>',
     '<h4 class="chart-title" data-translate-key="results_dimensions_title">SDG Dimensions</h4>'),
    ('<h4 class="chart-title">SDG Performance Ranking</h4>',
     '<h4 class="chart-title" data-translate-key="results_ranking_title">SDG Performance Ranking</h4>'),
    # Table section title & export
    ('                        Detailed SDG Scores\n',
     '                        <span data-translate-key="results_ranking_title">Detailed SDG Scores</span>\n'),
    ('<i class="fas fa-file-csv me-1"></i> Export All Data',
     '<i class="fas fa-file-csv me-1"></i> <span data-translate-key="results_export_btn">Export All Data</span>'),
    # Table headers
    ('<th scope="col">Name</th>',
     '<th scope="col" data-translate-key="results_col_name">Name</th>'),
    ('                                    Direct Score\n',
     '                                    <span data-translate-key="results_col_direct">Direct Score</span>\n'),
    ('                                    Bonus Score\n',
     '                                    <span data-translate-key="results_col_bonus">Bonus Score</span>\n'),
    ('                                    Total Score\n',
     '                                    <span data-translate-key="results_col_total">Total Score</span>\n'),
    ('<th scope="col" class="text-center" style="width: 150px;">Performance Bar</th>',
     '<th scope="col" class="text-center" style="width: 150px;" data-translate-key="results_col_performance">Performance</th>'),
    # No scores message
    ('<td colspan="6" class="text-center fst-italic text-muted py-4">No SDG scores available...</td>',
     '<td colspan="6" class="text-center fst-italic text-muted py-4" data-translate-key="results_no_scores">No SDG scores available...</td>'),
    # Recommendations
    ('                    Tailored Recommendations\n',
     '                    <span data-translate-key="results_recommendations_title">Tailored Recommendations</span>\n'),
    ('<p class="text-muted fst-italic mt-3">Recommendations cannot be generated as no scores are available.</p>',
     '<p class="text-muted fst-italic mt-3" data-translate-key="results_no_recommendations">Recommendations cannot be generated as no scores are available.</p>'),
    # Learn more
    ('<h5 class="mb-3">Learn More &amp; Improve Your Project</h5>',
     '<h5 class="mb-3" data-translate-key="results_learn_more_title">Learn More &amp; Improve Your Project</h5>'),
    # Share modal
    ('<h5 class="modal-title" id="shareModalLabel">Share Assessment Results</h5>',
     '<h5 class="modal-title" id="shareModalLabel" data-translate-key="results_share_title">Share Assessment Results</h5>'),
    ('<p class="text-muted">Share this assessment with others using the link below. The link will expire in 30 days.</p>',
     '<p class="text-muted" data-translate-key="results_share_desc">Share this assessment with others using the link below. The link will expire in 30 days.</p>'),
    ('<label for="shareUrl" class="form-label">Shareable Link</label>',
     '<label for="shareUrl" class="form-label" data-translate-key="results_share_link_label">Shareable Link</label>'),
    ('<i class="fas fa-copy me-2"></i>Copy Link',
     '<i class="fas fa-copy me-2"></i><span data-translate-key="results_copy_link_btn">Copy Link</span>'),
    ('<small class="text-muted">Anyone with this link can view the results (read-only)</small>',
     '<small class="text-muted" data-translate-key="results_share_readonly">Anyone with this link can view the results (read-only)</small>'),
    # Modals close/download
    ('<h5 class="modal-title" id="chartModalLabel">Chart View</h5>',
     '<h5 class="modal-title" id="chartModalLabel" data-translate-key="results_chart_view">Chart View</h5>'),
    ('<i class="fas fa-download me-1"></i> Download Chart',
     '<i class="fas fa-download me-1"></i> <span data-translate-key="results_download_chart">Download Chart</span>'),
]

# Apply replacements only for lines that don't already have data-translate-key
for old, new in replacements:
    if old in html and new not in html:
        html = html.replace(old, new, 1)

# Add "Close" translate keys to modal footer buttons (there are two)
html = re.sub(
    r'(<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">)Close(</button>)',
    r'\1<span data-translate-key="results_close_btn">Close</span>\2',
    html
)

# Add all Save Image buttons (multiple occurrences)
html = re.sub(
    r'(<i class="fas fa-download me-1"></i>) Save Image',
    r'\1 <span data-translate-key="results_save_image_btn">Save Image</span>',
    html
)

# Add i18n scripts before {% endblock %}
scripts_block = '{% block scripts %}\n{{ super() }}'
i18n_scripts = (
    '{% block scripts %}\n{{ super() }}\n'
    '    <script src="{{ url_for(\'static\', filename=\'js/assessment/i18n_assessment.js\') }}" defer></script>\n'
    '    <script src="{{ url_for(\'static\', filename=\'js/assessment/ui_assessment.js\') }}" defer></script>'
)
html = html.replace(scripts_block, i18n_scripts, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(html)

print("Done patching", path)

# Quick verification
count = html.count('data-translate-key=')
print(f"Total data-translate-key attrs: {count}")
i18n_ok = 'i18n_assessment.js' in html and 'ui_assessment.js' in html
print(f"i18n scripts added: {i18n_ok}")
