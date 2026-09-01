from models import EvidenceExtractionResult


def extract_evidence(
        raw_text: str,
        extraction_rules: str,
        client,
        model: str,
        llm_input_text: str | None = None,
) -> EvidenceExtractionResult:
    """Extract grounded evidence from raw source text."""

    input_text = (
        llm_input_text
        if llm_input_text is not None
        else raw_text
    )

    response = client.responses.parse(
        model=model,
        instructions=extraction_rules,
        input=input_text,
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


def select_candidate_text(
        raw_text: str,
) -> str:
    """Select candidate paragraphs for LLM evidence extraction."""

    candidate_keywords = [
        "AI",
        "大模型",
        "人工智能",
    ]

    paragraphs = raw_text.split("\n")

    selected_indexes = set()

    for index, paragraph in enumerate(paragraphs):
        if any(
            keyword in paragraph
            for keyword in candidate_keywords
        ):
            if index > 0:
                selected_indexes.add(index - 1)

            selected_indexes.add(index)

            if index < (len(paragraphs) - 1):
                selected_indexes.add(index + 1)

    selected_paragraphs = [
        paragraph
        for index, paragraph in enumerate(paragraphs)
        if index in selected_indexes
    ]

    return "\n".join(selected_paragraphs)

