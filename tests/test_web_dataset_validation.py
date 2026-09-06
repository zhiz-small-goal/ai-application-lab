from dataset_validation import validate_evidence_in_reference 

from models import (
    ExpectedEvidence,
    DatasetValidationResult,
    EvidenceSupport
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
        reason=None
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

    assert check_result.status is None
