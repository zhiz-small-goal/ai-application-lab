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


def rerank_chunks(
        chunks: list[Chunk],
        query: str,
        reranker: FlagReranker,
) -> list[dict]:
    """
    Rank chunks by relevance score for viven query.

    Args:
        chunks: Candidate chunks to be ranked.
        query: Query used to calculate chunk revlevance.

    Returns:
        A ranked list of chnks with their relevance scores.
    """

    pairs = [
        [query, chunk.text]
        for chunk in chunks
    ]

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
    

def display_ranked_chunks(
        results: list[dict]
):
    """
    Display ranked retrieval results for inspection.

    This function is used for debugging and experiment analysis.
    It shows the ranking order, reranker score, chunk provenance,
    and a short preview of chunk content.

    The output helps compare how different parsers affect:
    - retrieved chunk ranking;
    - relevance score distribution;
    - retrieved context quality.

    Args:
        results:
            Ranked chunks returned by rerank_chunks().
            Each item contains:
            - chunk: original Chunk object with provenance information.
            - score: reranker relevance score.
    """

    for rank, item in enumerate(
        results,
        start=1,
    ):
        chunk = item["chunk"]
        score = item["score"]

        print("=" * 50)
        print(f"Rank: {rank}")
        print(f"Score: {score:6f}")
        print(f"Start: {chunk.start}")
        print(f"End: {chunk.end}")

        print("\nText preview: ")
        print(chunk.text[:200])


def calculate_text_compression_ratio(
        original_text: str,
        compressed_text: str,
) -> float:
    """
    Calculate text compression ratio.

    Measures how much the parser reduces the original text size.

    A smaller ratio means the parsed text contains less content
    compared with the original representation.

    Args:
        original_text:
            Reference text before compression.

        compressed_text:
            Parser output text.

    Returns:
        compressed_text_length / original_text_length
    """

    if not original_text:
        return 0.0

    return len(compressed_text) / len(original_text)


def calculate_context_size(
        results: list[dict],
        top_k: int,
) -> int:
    """
    Calculate total character size of retrieved chunks.

    This approximates the amount of context sent to LLM
    after retrieval.

    Args:
        results:
            Ranked chunks returned by rerank_chunks().

        top_k:
            Number of chunks selected.

    Returns:
        Total characters in selected chunks.
    """

    return sum(
        len(item["chunk"].text)
        for item in results[:top_k]
    )


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


document_id = expected_evidence[0].document_id


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
            document_id=document_id,
            text=evidence.text,
            supports=parser_supports,
        )
    )


reference_chunks = split_into_chunks(
    document_id=document_id,
    text=reference_text,
)


parser_chunks = split_into_chunks(
    document_id=document_id,
    text=parser_text,
)


reranker = FlagReranker(
    "BAAI/bge-reranker-v2-m3",
    use_fp16=False,
)


reference_results = rerank_chunks(
    chunks=reference_chunks,
    query=query,
    reranker=reranker,
)


parser_results = rerank_chunks(
    chunks=parser_chunks,
    query=query,
    reranker=reranker,
)


print(
    "Parser compression ratio:",
    calculate_text_compression_ratio(
        reference_text,
        parser_text,
    )
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

    reference_context_size = calculate_context_size(
        results=reference_results,
        top_k=top_k,
    )

    parser_context_size = calculate_context_size(
        results=parser_results,
        top_k=top_k,
    )

    print(
        "\nTop-K:",
        top_k,
        "\nReference context size: ",
        reference_context_size,

        "\nParser context size: ",
        parser_context_size,
        "\nReference_Top_recall@k: ",
        reference_hit,
        "\nParser_Top_recall@K: ",
        parser_hit,
    )

    print("\n")
    display_ranked_chunks(results=reference_results[:top_k])
    display_ranked_chunks(results=parser_results[:top_k])
    print("\n\n")


