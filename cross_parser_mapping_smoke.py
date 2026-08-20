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

evidence_text = evidences[0]

search_start = 0

while True:
    index = reference_text.find(
        evidence_text,
        search_start,
    )

    if index == -1:
        break

    end = index + len(evidence_text)

    print(
        "\nstart: ",
        index,
        "end: ",
        end,
    )

    print(
        repr(
            reference_text[
                max(0, index - 100):
                min(len(reference_text), end + 150)
            ]
        )
    )

    search_start = index + 1

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