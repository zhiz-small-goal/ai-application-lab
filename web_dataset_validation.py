from models import (
    DatasetValidationResult,
    ExpectedEvidence,
    EvidenceSupport,
)

from evidence_mapping import normalize_text_with_position_map


def validate_evidence_in_reference(
        reference_text: str,
        document_id: str,
        expected_evidence_texts: list[str],
) -> DatasetValidationResult:
    """Validate and map expected evidence against reference text."""

    normalized_reference_text, normalized_reference_position = normalize_text_with_position_map(
        text=reference_text
    )

    expected_evidence = []

    status = True

    reason = None

    for evidence_text in expected_evidence_texts:
        normalized_evidence, _ = normalize_text_with_position_map(text=evidence_text)

        if normalized_evidence not in normalized_reference_text:
            status = False

        start = 0

        reference_supports = []

        while True:
            index = normalized_reference_text.find(evidence_text, start)
            if index == -1:
                break

            start = index + 1

            normalized_reference_start = index
            normalized_reference_end = normalized_reference_start + len(evidence_text)

            reference_start = normalized_reference_position[index]
            reference_end = normalized_reference_position[
                normalized_reference_end - 1
            ] + 1

            reference_supports.append(
                EvidenceSupport(
                    start=reference_start,
                    end=reference_end,
                )
            )

        expected_evidence.append(
            ExpectedEvidence(
                document_id=document_id,
                text=evidence_text,
                supports=reference_supports,
            )
        )

    return DatasetValidationResult(
        status=status,\
        mapped_evidence=expected_evidence,
        reason=reason
    )



