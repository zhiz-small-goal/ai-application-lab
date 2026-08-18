from difflib import SequenceMatcher


def project_evidence_span(
        reference_text: str,
        reference_start: int,
        reference_end: int,
        parser_text: str,
) -> tuple[int, int] | None:
    """Project a reference evidence span into parser text coordinates."""

    matcher = SequenceMatcher(
        None,
        reference_text,
        parser_text,
        autojunk=False,
    )

    for block in matcher.get_matching_blocks():
        reference_block_start = block.a
        parser_block_start = block.b
        reference_block_end = (
            reference_block_start
            + block.size
        )

        if (
                reference_block_start <= reference_start
                and reference_end <= reference_block_end
        ):
                start_offsets = (
                reference_start - reference_block_start
                )
                end_offsets = (
                reference_end - reference_block_start
                )

                parser_start = (
                        parser_block_start
                        + start_offsets
                )

                parser_end = (
                        parser_block_start
                        + end_offsets
                )

                project_text = parser_text[
                        parser_start:parser_end
                ]
                expected_text = reference_text[
                        reference_start:reference_end
                ]

                if project_text != expected_text:
                        return None

                return parser_start, parser_end

    return None