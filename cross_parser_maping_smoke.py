from pathlib import Path

from bs4 import BeautifulSoup
from trafilatura import extract


html = Path(
    "evaluation_samples/"
    "hunan_ai_platform_2025.html"
).read_text(
    encoding="utf-8"
)

# BeautifulSoup baseline
soup = BeautifulSoup(
    html,
    "html.parser"
)

reference_text = soup.get_text(
    separator="\n",
    strip=True
)


parser_text = extract(
    html
)


print(type(reference_text))
print(len(reference_text))

print(type(parser_text))
if parser_text is not None:
    print(len(parser_text))