import scrapy
from scrapy.http import HtmlResponse
from productparser.items import ProductItem
from urllib.parse import urljoin
from scrapy.loader import ItemLoader


class LeroymerlinSpider(scrapy.Spider):

    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']
    # раздел "Электроинструменты"
    start_urls = ['https://leroymerlin.ru/catalogue/elektroinstrumenty']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.s15wh9uj_plp::attr(href)').extract()[-1]
        next_page = urljoin(response.url, next_page)
        yield response.follow(next_page, callback=self.parse)

        product_urls = response.css('a.nf842wf_plp::attr(href)').extract()
        for url in product_urls:
            yield response.follow(url, callback=self.product_parse)

    def product_parse(self, response: HtmlResponse):

        # добавление характеристик в класс ProductItem, которые ранее не встречались
        product_item = ProductItem()
        params = response.css('dt.def-list__term::text').extract()
        for param in params:
            if param not in product_item.fields:
                product_item.fields[param] = product_item.fields['param_processors']
        #
        item_loader = ItemLoader(item=product_item, response=response)
        #
        values = response.css('dd.def-list__definition::text').extract()
        for param, value in zip(params, values):
            item_loader.add_value(param, value)
        #
        item_loader.add_css('name', 'h1.header-2::text')
        item_loader.add_xpath('price', '//span[@slot="price"]/text()')
        item_loader.add_xpath('currency', '//span[@slot="currency"]/text()')
        item_loader.add_xpath('unit', '//span[@slot="unit"]/text()')
        item_loader.add_xpath('photos', '//picture[@slot="pictures"]/img[@alt="product image"]/@data-origin')

        yield item_loader.load_item()
