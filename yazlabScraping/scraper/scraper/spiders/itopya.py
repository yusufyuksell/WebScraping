
import scrapy
from pymongo import MongoClient
from scrapy import Request


def get_database():
    client = MongoClient(
        "")
    return client["Notebook"].get_collection("NotebookDetails")


class ItopyaSpider(scrapy.Spider):
    name = 'itopya'
    base_url = "https://www.itopya.com"
    page_number = 2
    start_urls = ["https://www.itopya.com/notebook_k14?sayfa=1"]
    dbmanager = get_database()

    def parse(self, response):
        notebooks = response.css('div.product')

        for notebook in notebooks:
            notebookItem = NotebookItem()

            notebookItem['title'] = notebook.css("div.product-body > a.title::text").extract_first()
            notebookItem['marka'] = str(notebookItem['title']).split(" ", 1)[0]
            notebookItem['model'] = ""
            notebookItem['operatingSystem'] = ""
            notebookItem['islemciTipi'] = ""
            notebookItem['islemciModeli'] = ""
            notebookItem['ram'] = ""
            notebookItem['diskBoyutu'] = ""
            notebookItem['diskTuru'] = ""
            notebookItem['ekranBoyutu'] = ""
            notebookItem['ekranKarti'] = ""

            notebookItem['puan'] = ""

            notebookItem['fiyat'] = notebook.css("div.price > strong::text").extract_first()

            linkUrl = notebook.css("div.product-body > a.title")
            notebookItem["url"] = self.base_url + linkUrl.xpath('.//@href').get()

            # linkImage = notebook.css("a.product-list__link")
            # notebookItem["image"] = linkImage.xpath('.//@href').get()
            notebookItem["image"] = notebook.css("a.image > img::attr(data-src)").get()

            yield Request(notebookItem["url"], meta={'item': notebookItem}, callback=self.parse_detail)

        next_page = "https://www.itopya.com/notebook_k14?sayfa=" + str(self.page_number)

        if self.page_number <= 6:
            yield response.follow(next_page, callback=self.parse)
            self.page_number += 1

    def parse_detail(self, response):
        notebookItem = response.request.meta['item']

        tempOS = str(response.xpath("//td[contains(text(),'İşletim Sistemi')]/../td/text()").get())
        if tempOS.__contains__("Windows"):
            notebookItem['operatingSystem'] = "Windows"
        elif tempOS.__contains__("macOS"):
            notebookItem['operatingSystem'] = "MacOS"
        else:
            notebookItem['operatingSystem'] = "FreeDOS"

        notebookItem['islemciTipi'] = response.xpath("//td[contains(text(),'İşlemci Serisi')]/../td").get()
        notebookItem['islemciModeli'] = response.xpath("//td[contains(text(),'İşlemci Modeli')]/../td").get()
        notebookItem['ram'] = response.xpath("//td[contains(text(),'Ram Kapasitesi')]/../td").get()
        notebookItem['diskBoyutu'] = response.xpath("//td[contains(text(),'SSD')]/../td").get()

        tempType = str(notebookItem['title'])

        if tempType.__contains__("SSD"):
            notebookItem['diskTuru'] = "SSD"
        elif tempType.__contains__("HDD"):
            notebookItem['diskTuru'] = "HDD"

        notebookItem['ekranBoyutu'] = response.xpath("//td[contains(text(),'Ekran Boyutu')]/../td/text()").get()
        notebookItem['ekranKarti'] = response.xpath("//td[contains(text(),'GPU Model')]/../td/text()").get()

        yield {
            "title":notebookItem['title'],
            "marka":notebookItem['marka'],
            "model":notebookItem['model'],
            "op ses":notebookItem['operatingSystem'],
            "islemtip":notebookItem['islemciTipi'],
            "ismod":notebookItem['islemciModeli'],
            "ram":notebookItem['ram'],
            "diskboy":notebookItem['diskBoyutu'],
            "disk":notebookItem['diskTuru'],
            "ek boy":notebookItem['ekranBoyutu'],
            "ek kart":notebookItem['ekranKarti'],
            "puan":notebookItem['puan'],
            "fiyat":notebookItem['fiyat'],
            "url":notebookItem['url'],
            "image":notebookItem['image']
        }


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