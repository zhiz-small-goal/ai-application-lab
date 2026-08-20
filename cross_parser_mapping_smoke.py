from pathlib import Path

from bs4 import BeautifulSoup
from trafilatura import extract

from evidence_mapping import project_evidence_span


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


evidences = [
    "湖南银行2025人工智能管理平台研发服务项目",
    "公开招标采购",
    "项目预算：60万元",
    "供应商参与投标",
]


expected_evidence = [
    ("湖南银行2025人工智能管理平台研发服务项目", 3202, 3224),
    ("公开招标采购", 3299, 3305),
    ("供应商参与投标", 3316, 3323),
    ("项目预算：60万元", 3385, 3394),
]


reference_position = []




for evidence_text, start, end in expected_evidence: 

    parser_position = project_evidence_span(
        reference_text=reference_text,
        reference_start=start,
        reference_end=end,
        parser_text=parser_text,
    )

    if parser_position is None:

        print(
            evidence_text,
            "is not in reference text or parser text.\n"
                  ) 
        continue

    parser_start, parser_end = parser_position

    parser_evidence = parser_text[parser_start:parser_end] 

    assert parser_evidence == evidence_text