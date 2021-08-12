import scrapy
from urllib.parse import urljoin
from scrapy.http import HtmlResponse
from opendata.items import OpendataItem
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst

class RosstatSpider(scrapy.Spider):
    name = 'rosstat'
    allowed_domains = ['rosstat.gov.ru']
    # поиск по слову "брак"
    start_urls = ['https://rosstat.gov.ru/opendata?search=%D0%B1%D1%80%D0%B0%D0%BA']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//div[@class="pagination__item "]/a[text()="Далее"]/@href').extract_first()
        next_page = urljoin(response.url, next_page)
        yield response.follow(next_page, callback=self.parse)
        data_urls = response.css('a.card-opendata__title-link::attr(href)').extract()
        for url in data_urls:
            yield response.follow(url, callback=self.data_parse)

    def data_parse(self, response: HtmlResponse):

        item_loader = ItemLoader(item=OpendataItem(), response=response)
        item_loader.add_css('name', 'div.title-page h1::text')
        item_loader.add_xpath('number', '//td[@property="dc:identifier"]/text()')
        item_loader.add_xpath('file', '//div[@class="document-list__item"][position()=3]/div/a/@href')
        item_loader.default_output_processor = TakeFirst()
        yield item_loader.load_item()
