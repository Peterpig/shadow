# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    id = scrapy.Field()
    name = scrapy.Field()
    img_url = scrapy.Field()
    run_time = scrapy.Field()
    add_time = scrapy.Field()
    genre = scrapy.Field()
    release_date = scrapy.Field()
    
