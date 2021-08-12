import scrapy


class OpendataItem(scrapy.Item):

    name = scrapy.Field()
    number = scrapy.Field()
    file = scrapy.Field()
