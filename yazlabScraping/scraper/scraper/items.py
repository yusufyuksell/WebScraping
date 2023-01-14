# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NotebookItem(scrapy.Item):
    title = scrapy.Field()
    marka = scrapy.Field()
    model = scrapy.Field()
    operatingSystem = scrapy.Field()
    islemciTipi = scrapy.Field()
    islemciModeli = scrapy.Field()
    ram = scrapy.Field()
    diskBoyutu = scrapy.Field()
    diskTuru = scrapy.Field()
    ekranBoyutu = scrapy.Field()
    ekranKarti = scrapy.Field()
    puan = scrapy.Field()
    fiyat = scrapy.Field()
    url = scrapy.Field()
    image = scrapy.Field()

