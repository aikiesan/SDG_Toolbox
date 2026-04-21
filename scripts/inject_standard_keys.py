"""
Injects data-translate-key attributes into the Standard Assessment questionnaire HTML.
Uses BeautifulSoup to avoid regex-induced corruption. Safe to re-run (idempotent).
"""
import re
from bs4 import BeautifulSoup

HTML_PATH = "app/templates/questionnaire/assessment.html"

with open(HTML_PATH, encoding="utf-8") as f:
    content = f.read()

soup = BeautifulSoup(content, "html.parser")

# --- Section headings (section1_title ... section7_title) ---
for h2 in soup.find_all("h2", class_="tool-section-title"):
    h2_id = h2.get("id", "")
    m = re.match(r"section(\d+)-heading", h2_id)
    if m:
        h2["data-translate-key"] = f"section{m.group(1)}_title"

# --- Per-question elements ---
for container in soup.find_all("div", class_="question", id=re.compile(r"^q\d+-container$")):
    cid = container["id"]  # e.g. "q14-container"
    n = re.match(r"q(\d+)-container", cid).group(1)

    # Question text
    p_text = container.find("p", class_="question-text")
    if p_text:
        p_text["data-translate-key"] = f"q{n}_text"

    # Tooltip text inside .help-tooltip
    tooltip_wrapper = container.find(class_="help-tooltip")
    if tooltip_wrapper:
        tooltip_span = tooltip_wrapper.find("span", class_="tooltip-text")
        if tooltip_span:
            tooltip_span["data-translate-key"] = f"q{n}_help"

    # Option labels — id pattern: q{n}-opt{m}
    for label in container.find_all("label", attrs={"for": re.compile(rf"^q{n}-opt\d+$")}):
        for_val = label["for"]  # e.g. "q14-opt3"
        m_opt = re.match(rf"q{n}-opt(\d+)", for_val)
        if m_opt:
            label["data-translate-key"] = f"q{n}_opt{m_opt.group(1)}"

    # Select-type indicator spans
    radio_span = container.find("span", class_="radio-indicator")
    if radio_span:
        radio_span["data-translate-key"] = "select_one_option"

    checkbox_span = container.find("span", class_="checkbox-indicator")
    if checkbox_span:
        checkbox_span["data-translate-key"] = "select_all_options"

# Serialize — html.parser doesn't add doctype/html/body wrappers if not present
output = str(soup)

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(output)

print("Done. Translate keys injected into", HTML_PATH)

# Summary
soup2 = BeautifulSoup(output, "html.parser")
keyed = soup2.find_all(attrs={"data-translate-key": True})
print(f"Total elements with data-translate-key: {len(keyed)}")
