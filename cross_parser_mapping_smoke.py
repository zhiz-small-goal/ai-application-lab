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


reference_position = []

for evidence_text in evidences:

    count = reference_text.count(evidence_text)

    print(
        "evidence: ",
        evidence_text,
        "count: ",
        count
    )

    assert count == 1

    reference_start = reference_text.index(evidence_text)
    reference_end = reference_start + len(evidence_text)

    print(reference_start, reference_end)
    print(reference_text[reference_start:reference_end])
    reference_position.append((reference_start, reference_end))

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