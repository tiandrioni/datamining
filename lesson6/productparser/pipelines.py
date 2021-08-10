# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
import os
from urllib.parse import urlparse


class DataBasePipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client.leroymerlin_db

    def process_item(self, item, spider):
        collection = self.db['power_tools']
        collection.insert_one(ItemAdapter(item).asdict())

        return item


class PhotoPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None, *, item=None):
        return f'power_tools/{item["name"]} - {item["price"]} {item["currency"]}' \
               f'/{os.path.basename(urlparse(request.url).path)}'

    def get_media_requests(self, item, info):
        if item['photos']:
            for url in item['photos']:
                try:
                    yield scrapy.Request(url)
                except Exception:
                    print(Exception)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]

        return item

