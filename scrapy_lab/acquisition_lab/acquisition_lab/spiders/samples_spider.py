import json
from datetime import datetime, timezone
from pathlib import Path

import scrapy
from scrapy.linkextractors import LinkExtractor

from hashlib import sha256


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
                    "base_document_id": sample["document_id"],
                    "source_url": sample["source_url"],
                    "follow_selector": sample["follow_selector"],
                    "discovered_from_url": None,
                },
            )

    def parse(
            self,
            response,
            base_document_id: str,
            source_url: str,
            follow_selector: str | None,
            discovered_from_url: str | None,
    ):
        FROZEN_HTML_DIR.mkdir(exist_ok=True)
        PROVENANCE_DIR.mkdir(exist_ok=True)

        url_hash = sha256(
            response.url.encode("utf-8")
        ).hexdigest()[:12]

        document_id = (
            f"{base_document_id}_p{url_hash}"
        )

        html_path = FROZEN_HTML_DIR / f"{document_id}.html"
        html_path.write_bytes(response.body)

        provenance = {
            "document_id": document_id,
            "source_url": source_url,
            "response_url": response.url,
            "discovered_from_url": discovered_from_url,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status_code": response.status,
            "crawl_depth": response.meta.get("depth", 0),
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
            "\nSaved %s from %s\n",
            document_id,
            response.url,
        )

        link_extractor = LinkExtractor(
            allow_domains=["docs.python.org"],
            allow=(r"/3/library/.*\.html$",),
        )

        links = link_extractor.extract_links(response)

        self.logger.info(
            "Found %d candidate links from %s",
            len(links),
            response.url,
        )

        for link in links[:10]:
            yield response.follow(
                link,
                callback=self.parse,
                cb_kwargs={
                    "base_document_id": document_id,
                    "source_url": source_url,
                    "follow_selector": follow_selector,
                    "discovered_from_url": response.url,
                },
            )