import httpx

from pathlib import Path


from web_source_reader import read_web_source
from FlagEmbedding import FlagReranker
from chunking import split_into_chunks, calculate_evidence_recall
from models import ExpectedEvidence
from content_reader import read_text_content


client = httpx.Client()





expected_evidence = [
    ExpectedEvidence(
        document_id="doc001",
        text="湖南银行2025人工智能管理平台研发服务项目",
        start=3202,
        end=3224,
    ),
    ExpectedEvidence(
        document_id="doc001",
        text="公开招标采购",
        start=3299,
        end=3305,
    ),
    ExpectedEvidence(
        document_id="doc001",
        text="项目预算：60万元",
        start=3385,
        end=3394,
    ),
    ExpectedEvidence(
        document_id="doc001",
        text="供应商参与投标",
        start=3316,
        end=3323,
    ), 
]


raw_text = read_text_content(
    Path(
        "evaluation_samples/"
        "hunan_bank_ai_platform_2025.txt"
    )
)


for evidence in expected_evidence:
    assert(
        raw_text[evidence.start:evidence.end]
        == evidence.text
    )


query = (
    "寻找能够反映公司真实 AI 项目、业务应用、"
    "资源投入、采购或供应商关系以及业务结果的信息。"
)


chunks = split_into_chunks(
    text=raw_text,
    document_id="doc001",
)


pairs = [
    [query, chunk.text]
    for chunk in chunks
]


reranker = FlagReranker(
    "BAAI/bge-reranker-v2-m3",
    use_fp16=False
)


scores = reranker.compute_score(
    pairs,
    normalize=True
)


results = [
    {
        "chunk": chunk,
        "score": float(score),
    }
    for chunk, score in zip(
        chunks,
        scores,
    )
]


results.sort(
    key=lambda item: item["score"],
    reverse=True,
)


for top_k in [3, 5, 10, 20]:
    recall = calculate_evidence_recall(
        results=results,
        expected_evidence=expected_evidence,
        top_k=top_k,
    )

    selected_chars = sum(
        len(item["chunk"].text)
        for item in results[:top_k]
    )

    compression_ratio = (
        selected_chars / len(raw_text)
    )

    print(
        f"Top {top_k}: "
        f"recall={recall:.2%}, "
        f"compression={compression_ratio:.2%}"
    )


print("\nTop ranked chunks: ")

for rank, item in enumerate(
    results[:10],
    start=1,
):
    preview = item["chunk"].text.replace(
        "\n",
        "",
    )

    print(
        f"\nRank {rank}"
        f"\nScore: {item['score']:.10f}"
        f"\nText: {preview[:300]}"
    )


print("\nExpected evidence in raw text:")

for evidence in expected_evidence:
    print(
        evidence.text in raw_text,
        repr(evidence),
    )