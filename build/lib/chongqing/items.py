# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ChongqingItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    content = scrapy.Field()
    con_time = scrapy.Field()
    image = scrapy.Field()
    link = scrapy.Field()
    base = scrapy.Field()
    snid = scrapy.Field()
    stype = scrapy.Field()

