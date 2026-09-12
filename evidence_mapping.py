from difflib import Match, SequenceMatcher


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


class EvidenceSpanProjector:
    def __init__(
            self,
            reference_text: str,
            parser_text: str,
    ):
        self.reference_text = reference_text
        self.parser_text = parser_text

        self.normalized_reference_text, _ = normalize_text_with_position_map(self.reference_text)
        self.normalized_parser_text, self.parser_normalized_position = normalize_text_with_position_map(self.parser_text)

        self.matching_blocks = self.get_matching_blocks(
            original_text=self.normalized_reference_text,
            match_text=self.normalized_parser_text,
        )
        self.reference_boundary_map = self.get_boundary_map(self.reference_text)

    def project(
            self,
            reference_start: int,
            reference_end: int,
    ) -> tuple[int, int] | None:
        """Return span from parser text."""

        normalized_reference_start = self.reference_boundary_map[reference_start]
        normalized_reference_end = self.reference_boundary_map[reference_end]

        if normalized_reference_start == normalized_reference_end:
            return None

        for block in self.matching_blocks:
            reference_block_start = block.a
            reference_block_end = reference_block_start + block.size

            if (reference_block_start <= normalized_reference_start
                and reference_block_end >= normalized_reference_end):

                parser_block_start = block.b

                start_offset = normalized_reference_start - reference_block_start
                end_offset = normalized_reference_end - reference_block_start

                normalized_parser_start = parser_block_start + start_offset
                normalized_parser_end = parser_block_start + end_offset

                parser_start = self.parser_normalized_position[normalized_parser_start]
                parser_end = self.parser_normalized_position[
                    normalized_parser_end - 1
                ] + 1

                projected_text = self.parser_text[
                    parser_start:parser_end
                ]
                expected_text = self.reference_text[
                    reference_start:reference_end
                ]

                normalized_projected, _ = normalize_text_with_position_map(
                    projected_text
                )
                normalized_expected, _ = normalize_text_with_position_map(
                    expected_text
                )

                if normalized_projected != normalized_expected:
                    return None
                
                return parser_start, parser_end
        return None

    def get_boundary_map(
            self,
            text: str,
    ) -> list[int]:
        """
        Build a boundary map from the original text
        to the text with whitespace removed.

        boundary_map[k] represents the target boundary
        corresponding to source boundary k.
        """

        boundary_map = [0]
        text_position = 0

        for char in text:
            if not char.isspace():
                text_position += 1

            boundary_map.append(text_position)

        return boundary_map

    def get_matching_blocks(
            self,
            original_text: str,
            match_text: str,
    ) -> list[Match]:
        """Return matching blocks between two texts."""

        matcher = SequenceMatcher(
            None,
            original_text,
            match_text,
            autojunk=False,
        )

        return matcher.get_matching_blocks()
