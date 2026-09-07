from pathlib import Path
import json
import csv

from bs4 import BeautifulSoup
from trafilatura import extract

from FlagEmbedding import FlagReranker

from evidence_mapping import project_evidence_span, normalize_text_with_position_map
from dataset_validation import validate_evidence_in_reference, evaluate_parser_preservation
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


PROJECT_ROOT = Path(__file__).resolve().parent

samples_dir = PROJECT_ROOT / "evaluation_samples"


json_path = (
    PROJECT_ROOT
    / "evaluation_data"
    / "parser_evaluation_expected_evidence_v0.1.json"
)


with json_path.open(
    "r",
    encoding="utf-8",
) as file:
    dataset = json.load(file)

samples = dataset["samples"]


reranker = FlagReranker(
    "BAAI/bge-reranker-v2-m3",
    use_fp16=False,
    devices=["cuda:0"],
)

query = dataset["query"]


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

    parser_text = extract(sample_text)

    evidence_list = sample["expected_evidence"]

    document_id = sample["document_id"]

    expected_evidence_texts = []

    for evidence in evidence_list:
        expected_evidence_texts.append(evidence["text"])

    validate_reference = validate_evidence_in_reference(
    reference_text=reference_text,
    document_id=document_id,
    expected_evidence_texts=expected_evidence_texts,
    )

    if validate_reference.status is False:
        compression_ratio = calculate_text_compression_ratio(
            original_text=reference_text,
            compressed_text=parser_text,
        )

        evaluation_results.append(
            {
                "sample_id": sample["sample_id"],
                "filename": document_id,
                "top_k": None,

                "reference_status": False,
                "reference_validate_reason": validate_reference.reason,

                "expected_evidence_count": len(expected_evidence_texts),
                "reference_preserved_evidence_count": len(validate_reference.mapped_evidence),

                "parser_preserved_evidence_count": None,
                "reference_recall": None,
                "parser_recall": None,

                "parser_compression_ratio": compression_ratio,
            }
        )

        continue

    reference_evidence = validate_reference.mapped_evidence

    evaluate_parser = evaluate_parser_preservation(
        reference_text=reference_text,
        parser_text=parser_text,
        reference_evidence=reference_evidence
    )

    parser_evidence = evaluate_parser.mapped_evidence

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

        if parser_evidence:
            parser_hit = calculate_evidence_recall(
                results=parser_results,
                expected_evidence=parser_evidence,
                top_k=top_k,
            )
        else:
            parser_hit = None

        compression_ratio = calculate_text_compression_ratio(
            original_text=reference_text,
            compressed_text=parser_text,
        )

        evaluation_results.append(
            {
                "sample_id": sample["sample_id"],
                "filename": document_id,
                "top_k": top_k,

                "reference_status": True,
                "reference_validate_reason": validate_reference.reason,

                "expected_evidence_count": len(expected_evidence_texts),
                "reference_preserved_evidence_count": len(validate_reference.mapped_evidence),

                "parser_preserved_evidence_count": len(parser_evidence),
                "reference_recall": reference_hit,
                "parser_recall": parser_hit,

                "parser_compression_ratio": compression_ratio,
            }
        )


results_dir = PROJECT_ROOT / "results"
results_dir.mkdir(
    parents=True,
    exist_ok=True
)

output_path = (
    results_dir
    / "evaluation_results.csv"
)

with output_path.open(
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
        