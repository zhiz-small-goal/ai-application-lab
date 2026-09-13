from pathlib import Path

import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    async def start(self):
        urls = [
            "https://quotes.toscrape.com/page/1/",
        ]

        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
            )

    def parse(
            self,
            response,
    ):
        page = response.url.split("/")[-2]
        filename = f"quotes-{page}.html"

        Path(filename).write_bytes(
            response.body
        )

        self.logger.debug(
            "Save file %s",
            filename
        )

        next_page = response.css(
            "li.next a::attr(href)"
        ).get()

        if next_page is not None:
            yield response.follow(
                next_page,
                callback=self.parse,
            )