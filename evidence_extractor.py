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

    return response.output_parsed