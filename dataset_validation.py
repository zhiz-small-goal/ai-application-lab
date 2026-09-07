from models import (
    DatasetValidationResult,
    ExpectedEvidence,
    EvidenceSupport,
    MissingEvidenceSupport,
    ParserPreservationResult,
)

from evidence_mapping import normalize_text_with_position_map

from evidence_mapping  import project_evidence_span


def validate_evidence_in_reference(
        reference_text: str,
        document_id: str,
        expected_evidence_texts: list[str],
) -> DatasetValidationResult:
    """Validate and map expected evidence against reference text."""

    if not expected_evidence_texts:
        return DatasetValidationResult(
            status=False,
            mapped_evidence=[],
            reason="expected evidence is empty"
        )

    mapped_evidence = []

    status = True

    reason = ""

    missing_evidence = []

    normalized_reference_text, normalized_reference_position = normalize_text_with_position_map(
        text=reference_text
    )

    for evidence_text in expected_evidence_texts:
        normalized_evidence, _ = normalize_text_with_position_map(text=evidence_text)

        if normalized_evidence not in normalized_reference_text:
            status = False
            missing_evidence.append(evidence_text)
            continue

        start = 0

        reference_supports = []

        while True:
            index = normalized_reference_text.find(normalized_evidence, start)
            if index == -1:
                break

            start = index + 1

            normalized_reference_start = index
            normalized_reference_end = normalized_reference_start + len(normalized_evidence)

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

        mapped_evidence.append(
            ExpectedEvidence(
                document_id=document_id,
                text=evidence_text,
                supports=reference_supports,
            )
        )

    if missing_evidence:
        reason = (
            "Expected evidence not found in reference text: "
            + ", ".join(missing_evidence)
        )

    return DatasetValidationResult(
        status=status,
        mapped_evidence=mapped_evidence,
        reason=reason
    )


def evaluate_parser_preservation(
        reference_text: str,
        parser_text: str,
        reference_evidence: list[ExpectedEvidence]
) -> ParserPreservationResult:
    """Project reference evidence supports into parser text and record preservation results."""

    parser_mapped_evidence = []

    parser_missing_supports = []

    for evidence in reference_evidence:
        parser_supports = []

        evidence_text = evidence.text
        document_id = evidence.document_id

        for support in evidence.supports:
            reference_start = support.start
            reference_end = support.end

            parser_position = project_evidence_span(
                reference_text=reference_text,
                reference_start=reference_start,
                reference_end=reference_end,
                parser_text=parser_text,
            )

            if parser_position is None:
                parser_missing_supports.append(
                    MissingEvidenceSupport(
                        document_id=document_id,
                        evidence_text=evidence_text,
                        support=support,
                    )
                )
                continue

            parser_start, parser_end = parser_position

            parser_supports.append(
                EvidenceSupport(
                    start=parser_start,
                    end=parser_end,
                )
            )

        if parser_supports:
            parser_mapped_evidence.append(
                ExpectedEvidence(
                    document_id=document_id,
                    text=evidence_text,
                    supports=parser_supports,
                )
            )

    return ParserPreservationResult(
        mapped_evidence=parser_mapped_evidence,
        missing_supports=parser_missing_supports
    )

        


        




    
