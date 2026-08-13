import pytest

from evidence_extractor import extract_evidence, validate_evidence_grounding
from models import EvidenceCandidate, EvidenceExtractionResult


def test_extract_evidence_passes_expected_args():
    raw_text ="balabal"
    extract_rules = "you are beaultiful."
    expected_model = "test-model"

    class FakeResponse:
        output_parsed = EvidenceExtractionResult(
            evidence=[]
        )

    class FakeResponses:
        def parse(
                self,
                *,
                instructions: str,
                input: str,
                model: str,
                text_format,
        ):
            assert instructions == extract_rules
            assert input == raw_text
            assert model == expected_model
            assert text_format is EvidenceExtractionResult

            return FakeResponse()

    class FakeClient:
        responses = FakeResponses()

    extract_evidence(
        raw_text=raw_text,
        extraction_rules=extract_rules,
        client=FakeClient(),
        model=expected_model,
    )


def test_extract_evidence_returns_expected_result():
    raw_text = "Zhiz is learning AI application."
    extract_rules = "you are beautiful."
    model = "test-model"

    evidence_text = "Zhiz is learning AI."
    supporting_text = "Zhiz is learning AI application."

    expected_result = EvidenceExtractionResult(
        evidence=[EvidenceCandidate(
            evidence_text=evidence_text,
            supporting_text=supporting_text,
        )],
    )

    class FakeResponse:
        output_parsed = expected_result

    class FakeResponses:
        def parse(
            self,
            *,
            instructions: str,
            input: str,
            model: str,
            text_format,
        ):
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


def test_validate_evidence_grounding_rejects_non_grounded_supporting_text():
    raw_text = (
    "湖南银行正在采购人工智能管理平台研发服务。"
    "项目预算为60万元。"
    )
    supporting_text=(
    "湖南银行正在采购人工智能管理平台研发服务"
    "...项目预算为60万元"
    )

    with pytest.raises(ValueError):
        validate_evidence_grounding(
            raw_text=raw_text,
            supporting_text=supporting_text
        )

    
def test_extract_evidence_rejects_non_grounded_supporting_text():
    raw_text = "Zhiz is learning AI."
    evidence_text = "Zhiz is learning AI."
    supporting_text = "Zhiz is learning AI today."
    extract_rules = "hello."
    model = "test-model"

    expected_text = EvidenceExtractionResult(
        evidence=[
            EvidenceCandidate(
                evidence_text=evidence_text,
                supporting_text=supporting_text,
            )
        ]
    )

    class FakeResponse:
        output_parsed = expected_text

    class FakeResponses:
        def parse(
            self,
            *,
            input,
            instructions: str,
            model: str,
            text_format,
        ):
            return FakeResponse()

    class FakeClient:
        responses = FakeResponses()

    with pytest.raises(ValueError):
        extract_evidence(
            raw_text=raw_text,
            extraction_rules=extract_rules,
            client=FakeClient(),
            model=model,
        )


def test_validate_evidence_grounding_accepts_whitespace_differences():
    raw_text = (
        "湖南省招标有限责任公司受湖南银行股份有限公司的委托，对\n"
        "湖南银行2025人工智能管理平台研发服务项目\n"
        "进行公开招标采购"
    )

    supporting_text = (
        "湖南省招标有限责任公司受湖南银行股份有限公司的委托，"
        "对湖南银行2025人工智能管理平台研发服务项目进行公开招标采购"
    )

    validate_evidence_grounding(
        raw_text=raw_text,
        supporting_text=supporting_text,
    )


def test_extract_evidence_passes_llm_input_text():
    raw_text = "This is test raw text."
    llm_input_text = "Zhiz is beautiful."
    expected_result = EvidenceExtractionResult(
        evidence=[
            EvidenceCandidate(
                evidence_text="Zhiz is a woman.",
                supporting_text="This is test raw text."
            )
        ]
    )

    class FakeResponse:
        output_parsed = expected_result

    class FakeResponses:
        def parse(
                self,
                *,
                input: str,
                instructions: str,
                model: str,
                text_format,
        ):
            assert input == llm_input_text

            return FakeResponse()

    class FakeClient:
        responses = FakeResponses()

    extract_evidence(
        raw_text=raw_text,
        extraction_rules="test-extraction_rules",
        model="test-model",
        client=FakeClient(),
        llm_input_text=llm_input_text
    )
