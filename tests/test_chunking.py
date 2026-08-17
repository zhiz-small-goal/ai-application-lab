from chunking import split_into_chunks, chunk_covers_evidence, calculate_evidence_recall
from models import Chunk, ExpectedEvidence


def test_split_into_chunks_returns_expected_chunks_with_provenance():
    document_id = "doc-001"
    text = "abcdefghij"
    chunk_size = 4
    overlap = 1

    expected_chunks = [
        ("abcd", 0, 4),
        ("defg", 3, 7),
        ("ghij", 6, 10)
    ]

    chunks = split_into_chunks(
        document_id=document_id,
        text=text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    assert len(chunks) == len(expected_chunks)

    for chunk, (expected_text, expected_start, expected_end) in zip(
        chunks,
        expected_chunks,
    ):
        assert chunk.document_id == document_id
        assert chunk.text == expected_text
        assert chunk.start == expected_start
        assert chunk.end == expected_end
        assert chunk.text == text[chunk.start:chunk.end]

    for previous_chunk, current_chunk in zip(
        chunks,
        chunks[1:],
    ):
        assert previous_chunk.end - current_chunk.start == overlap


def test_chunk_covers_evidence_returns_true():
    chunk = Chunk(
        document_id="doc-001",
        text="abcdefgh",
        start=0,
        end=8,
    )

    evidence = ExpectedEvidence(
        document_id="doc-001",
        text="cdef",
        start=2,
        end=6,
    )

    result = chunk_covers_evidence(
        chunk=chunk,
        evidence=evidence,
    )

    assert result is True


def test_calculate_evidence_recall_returns_fraction_of_covered_evidence():
    expected_evidence = [
        ExpectedEvidence(
            document_id="doc-001",
            text="cdef",
            start=2,
            end=6,
        ),
        ExpectedEvidence(
            document_id="doc-001",
            text="ijkl",
            start=8,
            end=12,
        ),
    ]

    results = [
        {
            "chunk": Chunk(
                document_id="doc-001",
                text="abcdefgh",
                start=0,
                end=8,
            ),
            "score": 0.9
        },
        {
            "chunk": Chunk(
                document_id="doc-001",
                text="mnop",
                start=12,
                end=16,
            ),
            "score": 0.8
        },
    ]

    result = calculate_evidence_recall(
        results=results,
        expected_evidence=expected_evidence,
        top_k=2,
    )

    assert result == 0.5


def test_locate_evidence_span_whitespace_differences_returns_original_offsets():
    parsed_text = "前文项目预算：\n60万元后文"
    evidence_text = "项目预算：60万元"

    start, end = locate_evidence_span(
        parsed_text=parsed_text,
        evidence_text=evidence_text,
    )

    assert start == len("前文")
    assert end == len("前文项目预算：\n60万元")
