from difflib import SequenceMatcher


def normalize_text_with_position_map(
        text: str,
) -> tuple[str, list[int]]:
    """Remove whitespace and map normalized characters to original indexes."""

    normalized_chars = []
    position_map = []

    for index, char in enumerate(text):
        if char.isspace():
            continue

        normalized_chars.append(char)
        position_map.append(index)

    return "".join(normalized_chars), position_map


def project_evidence_span(
        reference_text: str,
        reference_start: int,
        reference_end: int,
        parser_text: str,
) -> tuple[int, int] | None:
    """Project a reference evidence span into parser text coordinates."""

    # Normalize both representations so whitespace-only differences
    # do not break otherwise equivalent text alignment.
    normalized_reference, _ = normalize_text_with_position_map(
        reference_text
    )
    normalized_parser, parser_position_map = (
        normalize_text_with_position_map(parser_text)
    )

    # Convert the original reference span boundaries into
    # normalized reference coordinates.
    normalized_reference_start = sum(
        not char.isspace()
        for char in reference_text[:reference_start]
    )
    normalized_reference_end = sum(
        not char.isspace()
        for char in reference_text[:reference_end]
    )

    # An evidence span containing only whitespace cannot be mapped reliably.
    if normalized_reference_start == normalized_reference_end:
        return None

    matcher = SequenceMatcher(
        None,
        normalized_reference,
        normalized_parser,
        autojunk=False,
    )

    for block in matcher.get_matching_blocks():
        reference_block_start = block.a
        parser_block_start = block.b
        reference_block_end = (
            reference_block_start
            + block.size
        )

        # Only project evidence fully contained inside one equal block.
        if (
            reference_block_start <= normalized_reference_start
            and normalized_reference_end <= reference_block_end
        ):
            start_offset = (
                normalized_reference_start
                - reference_block_start
            )
            end_offset = (
                normalized_reference_end
                - reference_block_start
            )

            normalized_parser_start = (
                parser_block_start
                + start_offset
            )
            normalized_parser_end = (
                parser_block_start
                + end_offset
            )

            # Convert normalized parser coordinates back into
            # the original parser_text coordinate system.
            parser_start = parser_position_map[
                normalized_parser_start
            ]
            parser_end = (
                parser_position_map[
                    normalized_parser_end - 1
                ]
                + 1
            )

            projected_text = parser_text[
                parser_start:parser_end
            ]
            expected_text = reference_text[
                reference_start:reference_end
            ]

            # Final validation ignores whitespace differences only.
            normalized_projected, _ = (
                normalize_text_with_position_map(projected_text)
            )
            normalized_expected, _ = (
                normalize_text_with_position_map(expected_text)
            )

            if normalized_projected != normalized_expected:
                return None

            return parser_start, parser_end

    return None