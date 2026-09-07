from dataset_validation import (
    validate_evidence_in_reference,
    evaluate_parser_preservation,
)

from models import (
    ExpectedEvidence,
    DatasetValidationResult,
    EvidenceSupport,
    MissingEvidenceSupport,
    ParserPreservationResult
)


def test_validate_evidence_in_reference_returns_valid_result_when_all_evidence_is_found():
    expected_evidence_texts = [
        "nihao",
        "zhiz",
    ]

    expected_validate_result = DatasetValidationResult(
        status=True,
        mapped_evidence=[
            ExpectedEvidence(
                document_id="doc-001",
                text="nihao",
                supports=[
                    EvidenceSupport(
                        start=1,
                        end=6,
                    )
                ]
            ),
            ExpectedEvidence(
                document_id="doc-001",
                text="zhiz",
                supports=[
                    EvidenceSupport(
                        start=8,
                        end=12,
                    )
                ]
            )
        ],
        reason="",
    )

    reference_text = "enihaoiszhizma"

    check_result = validate_evidence_in_reference(
        reference_text=reference_text,
        document_id="doc-001",
        expected_evidence_texts=expected_evidence_texts
    )

    assert check_result == expected_validate_result


def test_validate_evidence_in_reference_returns_invalid_result_when_evidence_not_found():
    expected_evidence_texts = [
        "nihao",
        "zhiz love",
    ]
    
    reference_text = "enihaoiszhizma"

    check_result = validate_evidence_in_reference(
        reference_text=reference_text,
        document_id="doc-001",
        expected_evidence_texts=expected_evidence_texts
    )

    assert check_result.reason == "Expected evidence not found in reference text: zhiz love"

    assert len(check_result.mapped_evidence) == 1
    assert check_result.mapped_evidence[0].text == "nihao"

    assert check_result.status is False


def test_evaluate_parser_preservation_maps_all_supports_when_all_are_preserved():
    reference_text = "zhiz is learning AI lab. zhiz is very good!"
    parser_text = "Hi! zhiz is learning, zhiz is baby"
    reference_evidence = [
        ExpectedEvidence(
            document_id="doc-001",
            text="zhiz",
            supports=[
                EvidenceSupport(
                    start=0,
                    end=4,
                ),
                EvidenceSupport(
                    start=25,
                    end=29,
                )
            ]
        ),
        ExpectedEvidence(
            document_id="doc-001",
            text="learn",
            supports=[
                EvidenceSupport(
                    start=8,
                    end=13,
                )
            ]
        )
    ]

    expected_result = ParserPreservationResult(
        mapped_evidence=[
            ExpectedEvidence(
                document_id="doc-001",
                text="zhiz",
                supports=[
                    EvidenceSupport(
                        start=4,
                        end=8,
                    ),
                    EvidenceSupport(
                        start=22,
                        end=26,
                    )
                ]
            ),
            ExpectedEvidence(
                document_id="doc-001",
                text="learn",
                supports=[
                    EvidenceSupport(
                        start=12,
                        end=17,
                    )
                ]
            )
        ],
        missing_supports=[],
    )

    evaluate_result = evaluate_parser_preservation(
        reference_text=reference_text,
        parser_text=parser_text,
        reference_evidence=reference_evidence
    )

    assert evaluate_result == expected_result


def test_evaluate_parser_preservation_records_missing_supports():
    reference_text = "zhiz is learning AI lab. zhiz is very good!"
    parser_text = "Hi! zhiz is learing, zhi is baby"
    reference_evidence = [
        ExpectedEvidence(
            document_id="doc-001",
            text="zhiz",
            supports=[
                EvidenceSupport(
                    start=0,
                    end=4,
                ),
                EvidenceSupport(
                    start=25,
                    end=29,
                )
            ]
        ),
        ExpectedEvidence(
            document_id="doc-001",
            text="learn",
            supports=[
                EvidenceSupport(
                    start=8,
                    end=13,
                )
            ]
        )
    ]

    expected_result = ParserPreservationResult(
        mapped_evidence=[
            ExpectedEvidence(
                document_id="doc-001",
                text="zhiz",
                supports=[
                    EvidenceSupport(
                        start=4,
                        end=8,
                    ),
                ]
            ),
        ],
        missing_supports=[
            MissingEvidenceSupport(
                document_id="doc-001",
                evidence_text="zhiz",
                support=EvidenceSupport(
                    start=25,
                    end=29,
                )
            ),
            MissingEvidenceSupport(
                document_id="doc-001",
                evidence_text="learn",
                support=EvidenceSupport(
                    start=8,
                    end=13,
                )
            )
        ],
    )

    evaluate_result = evaluate_parser_preservation(
        reference_text=reference_text,
        parser_text=parser_text,
        reference_evidence=reference_evidence
    )

    assert len(evaluate_result.mapped_evidence) == 1
    assert len(evaluate_result.missing_supports) == 2

    assert evaluate_result == expected_result


def test_validate_evidence_in_reference_returns_invalid_when_expected_evidence_empty():
    reference_text = "zhiz is learning AI lab. zhiz is very good!"
    expected_evidence_texts = []

    validate_result = validate_evidence_in_reference(
        reference_text=reference_text,
        document_id="doc-001",
        expected_evidence_texts=expected_evidence_texts,
    )

    assert validate_result.status is False

    assert len(validate_result.mapped_evidence) == 0
    assert validate_result.reason == "expected evidence is empty"

