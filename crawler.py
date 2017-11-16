import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor


class Crawler(scrapy.Spider):
    name = 'Crawler'
    allowed_domains = ['toscrape.com']
    extractor = LinkExtractor(allow_domains=allowed_domains)
    login_url = 'http://quotes.toscrape.com/login'
    start_urls = ['http://quotes.toscrape.com']

    def start_requests(self):
        yield scrapy.Request(url=self.login_url, callback=self.login)

    def login(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            formdata={'username': 'foo', 'password': 'bar'},
            callback=self.parse
        )

    def after_login(self, response):
        if 'logout' not in response.body:
            self.logger.error("Login failed")

        self.logger.debug("Login successful")
        for url in self.start_urls:
            self.logger.debug("Starting scrape at: {}".format(url))
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for link in self.extractor.extract_links(response):
            self.logger.debug("Found link: {}".format(str(link)))
            yield scrapy.Request(url=link.url, callback=self.parse)


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
process.crawl(Crawler)
process.start()

