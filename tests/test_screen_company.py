from models import CompanyScreeningDecision, CompanyScreeningResult
from company_screening import screen_company


def test_screen_company_give_true_arg_to_client():
    company_name = "zhiz"
    evidence = [
        "Zhiz is learning AI.",
        "Zhiz is learning AI application.",
    ]
    screening_rules = "Zhiz is essential to study earnestly."
    model = "test-model"

    expected_result = CompanyScreeningResult(
        facts=[
            "Zhiz is learning AI.",
        ],
        inferences=[
            "Zhiz is studying AI serously.",
        ],
        unknowns=[],
        decision=CompanyScreeningDecision.KEEP,
        decision_reason="The evidence supports further investigation.",
        missing_evidence=[],
    )

    class FakeResponse:
        output_parsed = expected_result

    class FakeResponses:
        def parse(
                elsf,
                *,
                model: str,
                instructions: str,
                input: str,
                text_format,
        ):
            assert model == "test-model"
            assert instructions == screening_rules

            assert input == (
                "Company:\n"
                "zhiz\n\n"
                "Evidence:\n"
                "- Zhiz is learning AI.\n"
                "- Zhiz is learning AI application."
            )

            assert text_format is CompanyScreeningResult

            return FakeResponse()

    class FakeClient:
        responses = FakeResponses()

    result = screen_company(
        company=company_name,
        evidence=evidence,
        screening_rules=screening_rules,
        client=FakeClient(),
        model=model,
    )

    assert result == expected_result
