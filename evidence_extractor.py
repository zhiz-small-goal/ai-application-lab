from models import EvidenceExtractionResult


def extract_evidence(
        raw_text: str,
        extraction_rules: str,
        client,
        model: str,
) -> EvidenceExtractionResult:
    """Extract grounded evidence from raw source text."""

    response = client.responses.parse(
        model=model,
        instructions=extraction_rules,
        input=raw_text,
        text_format=EvidenceExtractionResult,
    )

    result = response.output_parsed

    for item in result.evidence:
        validate_evidence_grounding(
            raw_text=raw_text,
            supporting_text=item.supporting_text,
        )

    return result


def validate_evidence_grounding(
        raw_text: str,
        supporting_text: str,
) -> None:
    """Validate that supporting text appears verbatim in the raw source."""

    normalized_raw_text = "".join(
        raw_text.split()
    )
    normalized_supporting_text = "".join(
        supporting_text.split()
    )

    if normalized_supporting_text not in normalized_raw_text:
        raise ValueError(
            f"Supporting text is not grounded: {supporting_text!r}"
        )