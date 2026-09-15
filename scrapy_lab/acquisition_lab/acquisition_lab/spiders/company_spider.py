from datetime import datetime, timezone

import scrapy
from scrapy.linkextractors import LinkExtractor

import json
from pathlib import Path

from hashlib import sha256


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_PATH = PROJECT_ROOT / "company_sources.json"
FROZEN_HTML_DIR = PROJECT_ROOT / "company_frozen_html"
PROVENANCE_DIR = PROJECT_ROOT / "comapny_provenance"


DENY_URL_PATTERNS = (
    # Account / authentication
    r"/(?:login|logout|signin|sign-in|register|signup|account)(?:/|$|\?)",

    # Search / functional pages
    r"/search(?:/|$|\?)",

    # Shopping / transaction pages
    r"/(?:cart|checkout)(?:/|$|\?)",

    # Legal / policy pages
    r"/(?:privacy(?:-policy)?|terms(?:-of-service)?|cookie(?:-policy)?)(?:/|$|\?)",

    # Feeds
    r"/(?:feed|rss)(?:/|$|\?)",

    # Common CMS administration
    r"/wp-admin(?:/|$)",
    r"/wp-login\.php(?:$|\?)",
)

class CompanySpider(scrapy.Spider):
    name = "company"

    async def start(self):
        companies = json.loads(
            SOURCE_PATH.read_text(encoding="utf-8")
        )

        for company in companies:
            yield scrapy.Request(
                url=company["source_url"],
                callback=self.parse,
                cb_kwargs={
                    "base_company_name": company["company_name"],
                    "source_url": company["source_url"],
                    "allowed_domains": company["allowed_domains"],
                    "discovered_from_url": None,
                }
            )

    def parse(
            self,
            response,
            base_company_name,
            source_url,
            allowed_domains,
            discovered_from_url,
    ):
        FROZEN_HTML_DIR.mkdir(exist_ok=True)
        PROVENANCE_DIR.mkdir(exist_ok=True)

        url_hash = sha256(
            response.url.encode("utf-8")
        ).hexdigest()[:12]

        document_id = (
            f"{base_company_name}_{url_hash}"
        )

        html_path = FROZEN_HTML_DIR / f"{document_id}.html"
        html_path.write_bytes(response.body)

        provenance = {
            "document_id": document_id,
            "company_name": base_company_name,
            "source_url": source_url,
            "response_url": response.url,
            "discovered_from_url": discovered_from_url,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status_code": response.status,
            "crawl_depth": response.meta.get("depth", 0),
            "content_type": response.headers.get(
                "content-Type",
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
            "\nSaved %s from %s",
            document_id,
            response.url,
        )

        link_extractor = LinkExtractor(
            allow_domains=allowed_domains,
            deny=DENY_URL_PATTERNS,
        )

        links = link_extractor.extract_links(response)

        self.logger.info(
            "Found %s candidate links from %s\n",
            len(links),
            response.url,
        )

        for link in links:
            yield response.follow(
                url=link,
                callback=self.parse,
                cb_kwargs={
                    "base_company_name": base_company_name,
                    "source_url": source_url,
                    "allowed_domains": allowed_domains,
                    "discovered_from_url": response.url,
                }
            )