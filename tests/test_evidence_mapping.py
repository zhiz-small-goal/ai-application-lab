from evidence_mapping import EvidenceSpanProjector


def test_evidence_span_projector_projects_after_prefix_removed():
    reference_text = "NAV|AAA|EVIDENCE|BBB"
    parser_text = "AAA|EVIDENCE|BBB"

    projector = EvidenceSpanProjector(
        reference_text=reference_text,
        parser_text=parser_text
    )

    result = projector.project(
        reference_start=8,
        reference_end=16,
    )

    assert result == (4, 12)


def test_evidence_span_projector_projects_correct_duplicate_occurrence():
    reference_text = (
        "AAA|EVIDENCE|BBB|EVIDENCE|CCC"
    )
    parser_text = (
        "AAA|EVIDENCE|XXX|BBB|EVIDENCE|CCC"
    )

    projector = EvidenceSpanProjector(
        reference_text=reference_text,
        parser_text=parser_text,
    )

    result = projector.project(
        # Select the second EVIDENCE occurrence.
        reference_start=17,
        reference_end=25,
    )

    assert result == (21, 29)


def test_evidence_span_projector_projects_returns_none_when_target_evidence_is_removed():
    reference_text = (
            "AAA|EVIDENCE|BBB|EVIDENCE|CCC"
        )
    parser_text = (
        "AAA|EVIDENCE|BBB|CCC"
    )

    projector = EvidenceSpanProjector(
        reference_text=reference_text,
        parser_text=parser_text,
    )

    result = projector.project(
        # Select the second EVIDENCE occurrence.
        reference_start=17,
        reference_end=25,
    )

    assert result is None


def test_evidence_span_projector_projects_handles_whitespace_difference():
    reference_text = "AAA|EVI  DENCE|BBB"
    parser_text = "AAA|EVI DENCE|BBB"

    projector = EvidenceSpanProjector(
        reference_text=reference_text,
        parser_text=parser_text,
    )

    result = projector.project(
        reference_start=4,
        reference_end=14,
    )

    assert result == (4, 13)


