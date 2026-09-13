import scrapy


class RetryTestsSpider(scrapy.Spider):
    name = "retry_test"

    async def start(self):
        yield scrapy.Request(
            url="https://httpbin.org/status/503",
            callback=self.parse,
        )

    def parser(
            self,
            response,
    ):
        self.logger.info(
            "parse received status: %s",
            response.status
        )