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
    """Return whether one chunk fully covers any valid evidence support."""

    if chunk.document_id != evidence.document_id:
        return False

    for support in evidence.supports:
        if (
            chunk.start <= support.start
            and chunk.end >= support.end
        ):
            return True

    return False


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
                chunk=item["chunk"],
            )
            for item in results[:top_k]
        )

        if is_hit:
            hits += 1

    return hits / len(expected_evidence)


def locate_evidence_span(
        evidence_text: str,
        parsed_text: str,
) -> tuple[int, int] | None:
    """Locate evidence in parsed text and return its start and end offsets, or None if not found."""

    normalized_chars = []
    position_map = []

    for index, text in enumerate(parsed_text):
        if text.isspace():
            continue
        
        normalized_chars.append(text)
        position_map.append(index)

    normalized_evidence_text = ("".join(evidence_text.split()))
    normalized_parsed_text = "".join(normalized_chars)

    count = normalized_parsed_text.count(normalized_evidence_text)

    if count == 0:
        return None

    if count > 1:
        raise ValueError(
            f"Multiple evidence matches found: {count}"
        )

    normalized_start = normalized_parsed_text.find(normalized_evidence_text)

    original_start = position_map[normalized_start]
    original_end = position_map[normalized_start + len(normalized_evidence_text) - 1] + 1

    
    return (original_start, original_end,)





