# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random
import requests
import json

from scrapy import signals

from fake_useragent import UserAgent
from shadow.spiders.douban import DoubanSpider 


class ShadowSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
        

class RequestProxy(object):

    def __init__(self):
        pass
        # with open('/Users/orange/Dropbox/code/houduan/scrapy/proxyspider/proxy_list.txt') as f:
        #     self.proxy_list = [ip.split(' ')[0].strip() for ip in f]

    def process_request(self, request, spider):
        pass
        # r = requests.get('http://127.0.0.1:8000/?types=0&count=5&country=国内')
        # ip_ports = json.loads(r.text)
        # ip_ports = random.choice(ip_ports)
        # proxy = random.choice(self.proxy_list)
        # request.meta['proxy'] = 'http://' + proxy
        # print(request.meta['proxy'])
