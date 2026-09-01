from pathlib import Path

from bs4 import BeautifulSoup
from trafilatura import extract

from evidence_mapping import project_evidence_span
from models import EvidenceSupport, ExpectedEvidence


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


expected_evidence = [
    ExpectedEvidence(
        document_id="doc-001",
        text="湖南银行2025人工智能管理平台研发服务项目",
        supports=[
            EvidenceSupport(
                start=3202,
                end=3224,
            ),
            EvidenceSupport(
                start=3274,
                end=3296,
            ),
            EvidenceSupport(
                start=3333,
                end=3355,
            ),
        ],
    ),
    ExpectedEvidence(
        document_id="doc-001",
        text="公开招标采购",
        supports=[
            EvidenceSupport(
                start=3299,
                end=3305,
            )
        ]
    ),
    ExpectedEvidence(
        document_id="doc-001",
        text="供应商参与投标",
        supports=[
            EvidenceSupport(
                start=3316,
                end=3323,
            )
        ]
    ),
    ExpectedEvidence(
        document_id="doc-001",
        text="项目预算：60万元",
        supports=[
            EvidenceSupport(
                start=3385,
                end=3394,
            )
        ]
    ),
]


for expected in expected_evidence:
    parser_supports = []

    for support in expected.supports:

        parser_position = project_evidence_span(
            reference_text=reference_text,
            reference_start=support.start,
            reference_end=support.end,
            parser_text=parser_text,
        )

        if parser_position is None:
            continue

        parser_start, parser_end = parser_position

        parser_supports.append(
            EvidenceSupport(
                start=parser_start,
                end=parser_end,
            )
        )

    if not parser_supports:
        print(
            expected.text,
            "Mapping failed",
        )
        continue

    print(
        expected.text,
        "->",
        parser_supports,
    )