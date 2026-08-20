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
    assert reference_text[start:end] == evidence_text
    

for reference_offsets in reference_position:
    reference_start, reference_end = reference_offsets

    parser_position = project_evidence_span(
        reference_text=reference_text,
        reference_start=reference_start,
        reference_end=reference_end,
        parser_text=parser_text,
    )

    assert parser_position is not None

    parser_start, parser_end = parser_position

    projected_text = parser_text[
        parser_start:parser_end
    ]

    print("parser position: ", parser_position)
    print("projected text: ", projected_text)