import scrapy
from pymongo import MongoClient
from scrapy import Request


def get_database():
    client = MongoClient(
        "")
    return client["Notebook"].get_collection("NotebookDetails")


class IncehesapSpider(scrapy.Spider):
    name = 'incehesap'
    base_url = "https://www.incehesap.com"
    page_number = 2
    start_urls = ["https://www.incehesap.com/notebook-fiyatlari/sayfa-1"]
    dbmanager = get_database()

    def parse(self, response):
        notebooks = response.css('a.product.relative.group.grid.bg-white.gap-y-1.product.py-3')

        for notebook in notebooks:
            notebookItem = NotebookItem()

            notebookItem['title'] = ""
            notebookItem['marka'] = ""
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

            notebookItem['fiyat'] = ""

            linkUrl = notebook.css("a.product")
            notebookItem["url"] = self.base_url + linkUrl.xpath('.//@href').get()

            # linkImage = notebook.css("a.product-list__link")
            # notebookItem["image"] = linkImage.xpath('.//@href').get()
            notebookItem["image"] = ""

            yield Request(notebookItem["url"], meta={'item': notebookItem}, callback=self.parse_detail)

        next_page = "https://www.incehesap.com/notebook-fiyatlari/sayfa-" + str(self.page_number)

        if self.page_number <= 11:
            yield response.follow(next_page, callback=self.parse)
            self.page_number += 1


    def parse_detail(self, response):
        notebookItem = response.request.meta['item']

        notebookItem['title'] = str(response.xpath(
            "//h1[@itemprop = 'name']/text()").get()).replace("\n                ","").replace("            ","")
        notebookItem['marka'] = notebookItem['title'].split(' ', 1)[0]

        notebookItem['model'] = response.xpath(
            "//th[contains(text(),'Model Kodu')]/../td/text()").get().split(" ")[-1]

        tempOS = str(response.xpath(
            "//th[contains(text(),'İşletim Sistemi')]/../td/text()").get())
        if tempOS.__contains__("Windows"):
            notebookItem['operatingSystem'] = "Windows"
        elif tempOS.__contains__("macOS"):
            notebookItem['operatingSystem'] = "MacOS"
        else:
            notebookItem['operatingSystem'] = "FreeDOS"

        notebookItem['islemciTipi'] = response.xpath(
            "//th[contains(text(),'İşlemci')]/../td/text()").get()
        notebookItem['islemciModeli'] = response.xpath(
            "//th[contains(text(),'İşlemci Modeli')]/../td/text()").get()
        notebookItem['ram'] = str(response.xpath(
            "//th[contains(text(),'Sistem Belleği')]/../td/text()").get()).replace(" ","").replace("GB","")
        notebookItem['diskBoyutu'] = str(response.xpath(
            "//th[contains(text(),'SSD')]/../td/text()")[1].get()).replace(" ","").replace("GB","")

        tempType =  str(response.xpath(
            "//th[contains(text(),'Kapasite')]/../td/text()").get()).split(' ')[-1]

        if tempType.__contains__("SSD"):
            notebookItem['diskTuru'] = "SSD"
        elif tempType.__contains__("HDD"):
            notebookItem['diskTuru'] = "HDD"



        notebookItem['ekranBoyutu'] = str(response.xpath(
            "//th[contains(text(),'Ekran Özelliği')]/../td/text()").get()).replace("\"","")
        notebookItem['ekranKarti'] = str(response.xpath(
            "//th[contains(text(),'Ekran Kartı')]/../td/text()").get()).replace(" ", "", 1)

        notebookItem['puan'] = ""

        notebookItem['fiyat'] = str(response.css("div.price::text").extract_first()).replace("\n                            ","").replace(" TL                        ","").replace(".","")

        notebookItem["image"] = self.base_url + response.xpath(
            "//img[@itemprop = 'image']/@data-src").get()
        if self.dbmanager.count_documents({"model": {"$regex": notebookItem["model"]}, }) == 0:
            self.dbmanager.insert_one({
                "title": notebookItem['title'],
                "marka": notebookItem['marka'],
                "model": notebookItem['model'],
                "operatingSystem": notebookItem['operatingSystem'],
                "islemciTipi": notebookItem['islemciTipi'],
                "islemciModeli": notebookItem['islemciModeli'],
                "ram": notebookItem['ram'],
                "diskBoyutu": notebookItem['diskBoyutu'],
                "diskTuru": notebookItem['diskTuru'],
                "ekranBoyutu": notebookItem['ekranBoyutu'],
                "ekranKarti": notebookItem['ekranKarti'],
                "puan": notebookItem['puan'],
                "incehesapFiyat": notebookItem['fiyat'],
                "incehesap": True,
                "incehesapUrl": notebookItem['url'],
                "image": notebookItem['image']
            })
        else:
            self.dbmanager.update_one({"model": {"$regex": notebookItem["model"]}
                                       }, {"$set": {
                "incehesapFiyat": notebookItem['fiyat'],
                "incehesap": True,
                "incehesapUrl": notebookItem['url'],
            }, }, )


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
