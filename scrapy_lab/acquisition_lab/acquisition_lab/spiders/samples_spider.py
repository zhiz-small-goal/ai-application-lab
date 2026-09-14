import json
from datetime import datetime, timezone
from pathlib import Path

import scrapy


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCES_PATH = PROJECT_ROOT / "sample_sources.json"
FROZEN_HTML_DIR = PROJECT_ROOT / "frozen_html"
PROVENANCE_DIR = PROJECT_ROOT / "provenance"


class SamplesSpider(scrapy.Spider):
    name = "samples"

    async def start(self):
        samples = json.loads(
            SOURCES_PATH.read_text(encoding="utf-8")
        )

        for sample in samples:
            yield scrapy.Request(
                url=sample["source_url"],
                callback=self.parse,
                cb_kwargs={
                    "document_id": sample["document_id"],
                    "source_url": sample["source_url"],
                },
            )

    def parse(
            self,
            response,
            document_id: str,
            source_url: str,
    ):
        FROZEN_HTML_DIR.mkdir(exist_ok=True)
        PROVENANCE_DIR.mkdir(exist_ok=True)

        html_path = FROZEN_HTML_DIR / f"{document_id}.html"
        html_path.write_bytes(response.body)

        provenance = {
            "document_id": document_id,
            "source_url": source_url,
            "response_url": response.url,
            "fecched_at": datetime.now(timezone.utc).isoformat(),
            "status_code": response.status,
            "content_type": response.headers.get(
                "Content-Type",
                b"",
            ).decode("latin-1"),
        }

        provenance_path = PROVENANCE_DIR / f"{document_id}.json"
        provenance_path.write_text(
            json.dumps(
                provenance,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        self.logger.info(
            "Save sample %s from %s",
            document_id,
            response.url,
        )