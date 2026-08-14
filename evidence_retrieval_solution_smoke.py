import httpx

from web_source_reader import read_web_source
from FlagEmbedding import FlagReranker
from chunking import split_into_chunks


client = httpx.Client()





expected_evidence = [
    "湖南银行2025人工智能管理平台研发服务项目",
    "公开招标采购",
    "项目预算：60万元",
    "供应商参与投标",
]


raw_text = read_web_source(
    url="https://www.hunan-bank.com/96599/2025-11/21/"
        "article_2025112118011847442.shtml?sessionid=",
    client=client,
)


query = (
    "寻找能够反映公司真实 AI 项目、业务应用、"
    "资源投入、采购或供应商关系以及业务结果的信息。"
)


chunks = split_into_chunks(
    text=raw_text,
)


pairs = [
    [query, chunk]
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
        "text": chunk,
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


def calculate_recall(
        results: list[dict],
        expected_evidence: list[str],
        top_k: int,
) -> float:
    selected_text = "\n".join(
        item["text"]
        for item in results[:top_k]
    )

    hits = sum(
        evidence in selected_text
        for evidence in expected_evidence
    )

    return hits / len(expected_evidence)


for top_k in [3, 5, 10, 20]:
    recall = calculate_recall(
        results=results,
        expected_evidence=expected_evidence,
        top_k=top_k,
    )

    selected_chars = sum(
        len(item["text"])
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
    preview = item["text"].replace(
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
        evidence in raw_text,
        repr(evidence),
    )