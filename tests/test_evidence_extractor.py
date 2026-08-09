from evidence_extractor import extract_evidence
from models import EvidenceCandidate, EvidenceExtractionResult


def test_extract_evidence_give_true_arg_and_return_output_parsed():
    raw_text ="balabal"
    extract_rules = "you are beaultiful."
    model = "test-model"
    evidence_text = "bal"
    supporting_text = "enen"

    expected_result = EvidenceExtractionResult(
        evidence=[
            EvidenceCandidate(
                evidence_text=evidence_text,
                supporting_text=supporting_text,
            )
        ]
    )

    class FakeResponse:
        output_parsed = expected_result

    class FakeResponses:
        def parse(
                self,
                *,
                model: str,
                instructions: str,
                input: str,
                text_format: EvidenceExtractionResult,
        ):
            assert model == "test-model"
            assert instructions == extract_rules
            assert input == raw_text
            assert text_format is EvidenceExtractionResult

            return FakeResponse()

    class FakeClient:
        responses = FakeResponses()

    result = extract_evidence(
        raw_text=raw_text,
        extraction_rules=extract_rules,
        client=FakeClient(),
        model=model,
    )

    assert result == expected_result


    