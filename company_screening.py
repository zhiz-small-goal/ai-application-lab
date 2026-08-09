from models import CompanyScreeningResult


def screen_company(
        company: str,
        evidence: list[str],
        screening_rules: str,
        client,
        model: str,
) -> CompanyScreeningResult:
    evidence_text = "\n".join(
        f"- {item}"
        for item in evidence
    )

    input_text = (
        f"Company:\n{company}\n\n"
        f"Evidence:\n{evidence_text}"
    )
    
    response = client.responses.parse(
        model=model,
        instructions=screening_rules,
        input=input_text,
        text_format=CompanyScreeningResult
    )

    return response.output_parsed