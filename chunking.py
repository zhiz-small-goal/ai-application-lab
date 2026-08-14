from models import Chunk, ExpectedEvidence


def split_into_chunks(
        document_id: str,
        text: str,
        chunk_size: int = 800,
        overlap: int = 200,
) -> list[Chunk]:
    """Split source text into overlapping chunks with provenance offsets."""

    chunks = []

    start = 0

    while start < len(text):
        end = min(
            start + chunk_size,
            len(text),
        )

        chunks.append(
            Chunk(
                document_id=document_id,
                text=text[start:end],
                start=start,
                end=end,
            )
        )

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def chunk_covers_evidence(
        chunk: Chunk,
        evidence: ExpectedEvidence,
) -> bool:
    """Return whether one chunk fully covers an epected evidence span."""

    return(
        chunk.document_id == evidence.document_id
        and chunk.start <= evidence.start
        and chunk.end >= evidence.end
    )


def calculate_evidence_recall(
        results: list[dict],
        expected_evidence: list[ExpectedEvidence],
        top_k: int,
) -> float:
    """Calculate the fraction of expected evidence fully covered by top-k chunks."""

    hits = 0

    for evidence in expected_evidence:
        is_hit = any(
            chunk_covers_evidence(
                evidence=evidence,
                chunk=chunk,
            )
            for chunk in results[:top_k]
        )

        if is_hit:
            hits += 1

    return hits / len(expected_evidence)

