import scrapy
from pymongo import MongoClient

from scrapy import Request


def get_database():
    client = MongoClient(
        "")
    return client["Notebook"].get_collection("NotebookDetails")


class VatanSpider(scrapy.Spider):
    name = 'vatan'
    base_url = "https://www.vatanbilgisayar.com"
    page_number = 2
    start_urls = ["https://www.vatanbilgisayar.com/notebook/?page=1"]
    dbmanager = get_database()

    def parse(self, response):
        notebooks = response.css('div.product-list.product-list--list-page')

        for notebook in notebooks:
            notebookItem = NotebookItem()

            notebookItem['title'] = notebook.css("div.product-list__product-name > h3::text").extract_first()
            notebookItem['marka'] = \
                str(notebook.css("div.product-list__product-name > h3::text").extract_first()).split(' ', 1)[0]
            notebookItem['model'] = str(notebook.css("div.product-list__product-code::text").extract_first()).replace("\n", "").split(" ")[-1]
            notebookItem['operatingSystem'] = ""
            notebookItem['islemciTipi'] = ""
            notebookItem['islemciModeli'] = ""
            notebookItem['ram'] = ""
            notebookItem['diskBoyutu'] = ""
            notebookItem['diskTuru'] = ""
            notebookItem['ekranBoyutu'] = ""
            notebookItem['ekranKarti'] = ""

            notebookItem['puan'] = int(
                str(notebook.css('span.score').xpath("@style").get()).split(':')[1].split('%')[0]) / 20

            notebookItem['fiyat'] = notebook.css("span.product-list__price::text").extract_first().replace(".","")

            linkUrl = notebook.css("a.product-list__link")
            notebookItem["url"] = self.base_url + linkUrl.xpath('.//@href').get()

            # linkImage = notebook.css("a.product-list__link")
            # notebookItem["image"] = linkImage.xpath('.//@href').get()
            notebookItem["image"] = ""

            yield Request(notebookItem["url"], meta={'item': notebookItem}, callback=self.parse_detail)

        next_page = "https://www.vatanbilgisayar.com/notebook/?page=" + str(self.page_number)

        if self.page_number <= 18:
            yield response.follow(next_page, callback=self.parse)
            self.page_number += 1

    def parse_detail(self, response):
        notebookItem = response.request.meta['item']

        tempOS = str(response.xpath("//td[contains(text(),'İşletim Sistemi')]/../td/p/text()").get())
        if tempOS.__contains__("Windows"):
            notebookItem['operatingSystem'] = "Windows"
        elif tempOS.__contains__("macOS"):
            notebookItem['operatingSystem'] = "MacOS"
        else:
            notebookItem['operatingSystem'] = "FreeDOS"

        notebookItem['islemciTipi'] = response.xpath(
            "//td[contains(text(),'İşlemci Teknolojisi')]/../td/p/text()").get()
        notebookItem['islemciModeli'] = response.xpath("//td[contains(text(),'İşlemci Numarası')]/../td/p/text()").get()
        notebookItem['ram'] = str(
            response.xpath("//td[contains(text(),'Ram (Sistem Belleği)')]/../td/p/text()").get()).replace(" ",
                                                                                                          "").replace(
            "GB", "")
        notebookItem['diskBoyutu'] = response.xpath(
            "//td[contains(text(),'Disk Kapasitesi')]/../td/p/text()").get().replace(" ", "").replace("GB", "")

        tempType = str(response.xpath("//td[contains(text(),'Disk Türü')]/../td/p/text()").get())

        if tempType.__contains__("SSD"):
            notebookItem['diskTuru'] = "SSD"
        elif tempType.__contains__("HDD"):
            notebookItem['diskTuru'] = "HDD"

        notebookItem['ekranBoyutu'] = str(
            response.xpath("//td[contains(text(),'Ekran Boyutu')]/../td/p/text()").get()).replace(" inch", "")
        notebookItem['ekranKarti'] = response.xpath(
            "//td[contains(text(),'Ekran Kartı Chipseti')]/../td/p/text()").get()

        linkImage = response.css("div.swiper-slide")
        notebookItem["image"] = linkImage.xpath('.//@data-img').get()
        if self.dbmanager.count_documents({"model" :  { "$regex":notebookItem["model"]},}) == 0:
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
                "vatanFiyat": notebookItem['fiyat'],
                "vatan": True,
                "vatanUrl": notebookItem['url'],
                "image": notebookItem['image']
            })
        else:
            self.dbmanager.update_one({"model":{ "$regex":notebookItem["model"]}
                                       }, {"$set": {
                "islemciTipi": notebookItem['islemciTipi'],
                "islemciModeli": notebookItem['islemciModeli'],
                "ram": notebookItem['ram'],
                "diskBoyutu": notebookItem['diskBoyutu'],
                "diskTuru": notebookItem['diskTuru'],
                "ekranBoyutu": notebookItem['ekranBoyutu'],
                "ekranKarti": notebookItem['ekranKarti'],
                "puan": notebookItem['puan'],
                "vatanFiyat": notebookItem['fiyat'],
                "vatan": True,
                "vatanUrl": notebookItem['url'],
                "image": notebookItem['image']
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
