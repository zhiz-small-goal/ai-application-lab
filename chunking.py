from models import Chunk


def split_into_chunks(
        document_id: str,
        text: str,
        chunk_size: int = 800,
        overlap: int = 200,
) -> list[Chunk]:
    chunks = []

    start = 0

    while start < len(text):
        end = min(
            start + chunk_size,
            len(text),
        )

        chunks.append(
            Chunk(
                document_id=document_id,
                text=text[start:end],
                start=start,
                end=end,
            )
        )

        if end >= len(text):
            break

        start = end - overlap

    return chunks