from web_dataset_validation import validate_evidence_in_reference 

from models import (
    ExpectedEvidence,
    DatasetValidationResult,
    EvidenceSupport
)


def test_get_source_mismatch_returns_checked_result():
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
                        start=7,
                        end=11,
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