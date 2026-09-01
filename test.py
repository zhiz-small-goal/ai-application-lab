from pathlib import Path
import json
import csv

from bs4 import BeautifulSoup
from trafilatura import extract

from FlagEmbedding import FlagReranker

from evidence_mapping import project_evidence_span, normalize_text_with_position_map
from models import Chunk, EvidenceSupport, ExpectedEvidence

from chunking import calculate_evidence_recall, split_into_chunks


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


samples_dir = Path("e:\downld\parser_boundary_tests_v0.1")


json_path = Path("e:\downld\parser_boundary_tests_v0.1\parser_boundary_expected_evidence_v0.1.json")


with json_path.open(
    "r",
    encoding="utf-8",
) as file:
    dataset = json.load(file)

samples = dataset["samples"]


reranker = FlagReranker(
    "BAAI/bge-reranker-v2-m3",
    use_fp16=False,
)

query = "是否有 AI 资源投入？"


evaluation_results = []


for sample in samples:
    sample_file = samples_dir / (sample["file_name"])

    sample_text = sample_file.read_text(
        encoding="utf-8"
    )

    soup = BeautifulSoup(
        sample_text,
        "html.parser",
    )

    reference_text = soup.get_text(
        separator="\n",
        strip=True,
    )

    normalized_reference_text, normalized_reference_position = normalize_text_with_position_map(
        text=reference_text
    )

    parser_text = extract(sample_text)
    normalized_parser, _ = normalize_text_with_position_map(parser_text)

    evidence_list = sample["expected_evidence"]

    document_id = sample["document_id"]

    reference_evidence = []

    parser_project_evidence = []

    kipped_evidence = 0

    parser_kipped_evidence = []

    for evidence in evidence_list:

        reference_evidence_supports = []
        parser_evidence_supports = []

        evidence_text = evidence["text"]

        normalized_evidence, normalized_evidence_position = normalize_text_with_position_map(text=evidence_text)

        if normalized_evidence not in normalized_reference_text:
            print("Expected Evidence is not in Reference text!",repr(evidence_text), repr(sample_file))
            kipped_evidence += 1
            continue

        if normalized_evidence not in normalized_parser:
            print("Evidence is not in parser text")
            parser_kipped_evidence.append(normalized_evidence)
            kipped_evidence_start = reference_text.find(evidence_text)
            print("\n", normalized_evidence, kipped_evidence_start, document_id, "\n")

        normalized_reference_start = normalized_reference_text.find(normalized_evidence)
        normalized_reference_end = normalized_reference_start + len(normalized_evidence)

        reference_start = normalized_reference_position[
            normalized_reference_start
        ]

        reference_end = normalized_reference_position[
            normalized_reference_end - 1
        ] + 1
        

        reference_evidence_supports.append(
            EvidenceSupport(
                start=reference_start,
                end=reference_end,
            )
        )

        reference_evidence.append(
            ExpectedEvidence(
                document_id=document_id,
                text=evidence_text,
                supports=reference_evidence_supports,
            )
        )

        parser_position = project_evidence_span(
            reference_text=reference_text,
            reference_end=reference_end,
            reference_start=reference_start,
            parser_text=parser_text,
        )

        if parser_position is None:
            print("Mapping Failed")
            continue

        parser_start, parser_end = parser_position

        parser_evidence_supports.append(
            EvidenceSupport(
                start=parser_start,
                end=parser_end,
            )
        )

        parser_project_evidence.append(
            ExpectedEvidence(
                document_id=document_id,
                text=evidence_text,
                supports=parser_evidence_supports,
            )
        )

    print("\nKipped evidence: ", kipped_evidence)

    if len(reference_evidence) == 0:
        print("\nReference evidence is 0 range, document id is: ", document_id)
        continue

    if len(parser_project_evidence) == 0:
        print("\nParser evidence is 0 range")
        continue

    reference_chunks = split_into_chunks(
        document_id=document_id,
        text=reference_text,
    )

    parser_chunks = split_into_chunks(
        document_id=document_id,
        text=parser_text,
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

    for top_k in [3, 5, 7]:
        reference_hit = calculate_evidence_recall(
            results=reference_results,
            expected_evidence=reference_evidence,
            top_k=top_k,
        )

        parser_hit = calculate_evidence_recall(
            results=parser_results,
            expected_evidence=parser_project_evidence,
            top_k=top_k,
        )

        compression_ratio = calculate_text_compression_ratio(
            original_text=reference_text,
            compressed_text=parser_text,
        )

        evaluation_results.append(
            {
                "filename": document_id,
                "top_K": top_k,
                "expected_evidence_count": len(reference_evidence),
                "parser_preserved_evidence_count": len(parser_project_evidence),
                "reference_recall": reference_hit,
                "parser_recall": parser_hit,
                "parser_compression_ratio": compression_ratio,
            }
        )


print(len(evaluation_results))

with open(
    "evaluation_results.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=evaluation_results[0].keys()
    )

    writer.writeheader()
    writer.writerows(evaluation_results)

print("\nEvaluation results csv output")
        