from evidence_mapping import project_evidence_span


def test_project_evidence_span_projects_after_prefix_removed():
    reference_text = "NAV|AAA|EVIDENCE|BBB"
    parser_text = "AAA|EVIDENCE|BBB"

    result = project_evidence_span(
        reference_text=reference_text,
        reference_start=8,
        reference_end=16,
        parser_text=parser_text,
    )

    assert result == (4, 12)


def test_project_evidence_span_projects_coreect_duplicate_occurrence():
    reference_text = (
        "AAA|EVIDENCE|BBB|EVIDENCE|CCC"
    )
    parser_text = (
        "AAA|EVIDENCE|XXX|BBB|EVIDENCE|CCC"
    )

    result = project_evidence_span(
        reference_text=reference_text,
        # Select the second EVIDENCE occurrence.
        reference_start=17,
        reference_end=25,
        parser_text=parser_text,
    )

    assert result == (21, 29)


def test_project_evidence_span_returns_none_when_target_evidence_is_removed():
    reference_text = (
            "AAA|EVIDENCE|BBB|EVIDENCE|CCC"
        )
    parser_text = (
        "AAA|EVIDENCE|BBB|CCC"e
    )

    result = project_evidence_span(
        reference_text=reference_text,
        # Select the second EVIDENCE occurrence.
        reference_start=17,
        reference_end=25,
        parser_text=parser_text,
    )

    assert result is None

