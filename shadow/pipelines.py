# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

class MongoPipline(object):

    def __init__(self, mongo_uri, mongo_port, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_port = mongo_port
        self.mongo_db = mongo_db
        print(self.mongo_uri, self.mongo_db)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_port=crawler.settings.get('mongo_port', 27017),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host=self.mongo_uri,port=self.mongo_port)
        self.db = self.client[self.mongo_db]
        # 给spider设置唯一索引
        collection_name = spider.__class__.__name__.lower()
        self.db[collection_name].ensure_index('id', unique=True)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        collection_name = spider.__class__.__name__.lower()
        try:
            self.db[collection_name].insert(dict(item))
        except:
            pass
        return item
