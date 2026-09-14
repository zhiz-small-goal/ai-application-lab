from pathlib import Path

from html_parser import extract_text_from_html


raw_path = Path("scrapy_lab/acquisition_lab/rfc-rfc.html")

html = raw_path.read_text(
    encoding="utf-8",
)
print("HTML size: ", len(html))

parser_text = extract_text_from_html(
    html=html
)

print(type(parser_text))