# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from scrapy.pipelines.files import FilesPipeline
from urllib.parse import urlparse
import os
from pymongo import MongoClient


class DataBasePipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client.rosstat

    def process_item(self, item, spider):
        collection = self.db['search']
        collection.insert_one(ItemAdapter(item).asdict())

        return item


class FileOpendataPipeline(FilesPipeline):

    def file_path(self, request, response=None, info=None, *, item=None):
        return f'{item["number"]}.{os.path.basename(urlparse(request.url).path).split(".")[-1]}'

    def get_media_requests(self, item, info):
        url = item['file']
        if url:
            try:
                yield scrapy.Request(url)
            except Exception:
                print(Exception)

    def item_completed(self, results, item, info):
        if results:
            item['file'] = [itm[1] for itm in results if itm[0]]

        return item
