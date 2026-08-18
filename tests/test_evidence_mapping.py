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