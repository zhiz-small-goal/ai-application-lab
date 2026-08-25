from pathlib import Path
from bs4 import BeautifulSoup
from trafilatura import extract

from FlagEmbedding import FlagReranker

from evidence_mapping import project_evidence_span
from chunking import split_into_chunks, calculate_evidence_recall


from models import(
    EvidenceSupport,
    ExpectedEvidence,
    Chunk,
)


def evaluate_chunks(
        chunks: Chunk,
        query: str
) -> list[dict]:
    """Return evaluate result for chunks."""

    pairs = [
        [query, chunk.text]
        for chunk in chunks
    ]

    reranker = FlagReranker(
        "BAAI/bge-reranker-v2-m3",
        use_fp16=False,
    )

    scores = reranker.compute_score(
        pairs,
        normalize=True,
    )

    results = [
        {
            "chunk": chunk,
            "score": score,
        }
        for chunk, score in zip(
            chunks,
            scores,
        )
    ]

    results.sort(
        key=lambda item: float(item["score"]),
        reverse=True,
    )

    return results
    

html = Path("evaluation_samples/hunan_ai_platform_2025.html").read_text(
    encoding="utf-8"
)

soup = BeautifulSoup(
    html,
    "html.parser",
)

reference_text = soup.get_text(
    "\n",
    strip=True
)

parser_text = extract(
    html
)

assert parser_text is not None

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


doc_id = expected_evidence[0].document_id


query = "是否出现对人工智能有资源投入的信号？"


parser_project_evidence = []


for evidence in expected_evidence:
    parser_supports = []

    for support in evidence.supports:
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
            "Mapping failed: ",
            evidence,
        )
        continue

    parser_project_evidence.append(
        ExpectedEvidence(
            document_id=doc_id,
            text=evidence.text,
            supports=parser_supports,
        )
    )


reference_chunks = split_into_chunks(
    document_id=doc_id,
    text=reference_text,
)


parser_chunks = split_into_chunks(
    document_id=doc_id,
    text=parser_text,
)


reference_results = evaluate_chunks(
    chunks=reference_chunks,
    query=query,
)


parser_results = evaluate_chunks(
    chunks=parser_chunks,
    query=query
)


for top_k in [3, 5, 7]:
    reference_hit = calculate_evidence_recall(
        results=reference_results,
        expected_evidence=expected_evidence,
        top_k=top_k
    )

    parser_hit = calculate_evidence_recall(
        results=parser_results,
        expected_evidence=parser_project_evidence,
        top_k=top_k,
    )

    print(
        "\nTop-K:",
        top_k,
        "\nReference_Top_recall@k: ",
        reference_hit,
        "\nParser_Top_recall@K: ",
        parser_hit,
    )


