import scrapy
from scrapy.loader.processors import TakeFirst, MapCompose


def name_filter(name):
    return name.split(',')[0]


def price_filter(price):
    return int(''.join(price.split()))


def param_filter(param):
    param = param.strip()
    try:
        result = int(param)
    except ValueError:
        try:
            result = float(param)
        except ValueError:
            result = param
    return result


class ProductItem(scrapy.Item):
    _id =scrapy.Field()

    name = scrapy.Field(
        input_processor=MapCompose(name_filter),
        output_processor=TakeFirst()
    )

    price = scrapy.Field(
        input_processor=MapCompose(price_filter),
        output_processor=TakeFirst()
    )

    currency = scrapy.Field(
        output_processor=TakeFirst()
    )

    unit = scrapy.Field(
        output_processor=TakeFirst()
    )

    param_processors = scrapy.Field(
        input_processor=MapCompose(param_filter),
        output_processor=TakeFirst()
    )

    photos = scrapy.Field()
