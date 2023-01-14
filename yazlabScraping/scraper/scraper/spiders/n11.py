import scrapy
from pymongo import MongoClient
from scrapy import Request


def get_database():
    client = MongoClient(
        "")
    return client["Notebook"].get_collection("NotebookDetails")


class N11Spider(scrapy.Spider):
    name = 'n11'
    base_url = "https://www.n11.com"
    page_number = 2
    start_urls = ["https://www.n11.com/bilgisayar/dizustu-bilgisayar?m=Asus-Apple-Acer-Dell-Casper-Hometech-HP-Huawei-Msi-Dynabook&pg=1"]
    dbmanager = get_database()

    def parse(self, response):
        notebooks = response.css('li.column')

        for notebook in notebooks:
            notebookItem = NotebookItem()

            notebookItem['title'] = str(notebook.css("h3.productName::text").extract_first()).replace("\"", "")
            notebookItem['marka'] = \
                str(notebook.css("h3.productName::text").extract_first()).split(' ', 1)[0]
            notebookItem['model'] = ""

            notebookItem['operatingSystem'] = ""
            notebookItem['islemciTipi'] = ""
            notebookItem['islemciModeli'] = ""
            notebookItem['ram'] = ""
            notebookItem['diskBoyutu'] = ""
            notebookItem['diskTuru'] = ""
            notebookItem['ekranBoyutu'] = ""
            notebookItem['ekranKarti'] = ""

            notebookItem['puan'] = int(str(notebook.css('span.rating').xpath("@class").get()).split(' r')[1]) / 20

            notebookItem['fiyat'] = str(notebook.css("ins::text").extract_first()).replace(" TL", "").replace(".","")


            linkUrl = notebook.css("a.plink")
            notebookItem["url"] = linkUrl.xpath('.//@href').get()

           
            notebookItem["image"] = ""

            yield Request(notebookItem["url"], meta={'item': notebookItem}, callback=self.parse_detail)

        next_page = "https://www.n11.com/bilgisayar/dizustu-bilgisayar?m=Asus-Apple-Acer-Dell-Casper-Hometech-HP-Huawei-Msi-Dynabook&pg=" + str(self.page_number)

        if self.page_number <= 50:
            yield response.follow(next_page, callback=self.parse)
            self.page_number += 1

    def parse_detail(self, response):
        notebookItem = response.request.meta['item']

        notebookItem['model'] = str(response.xpath(
            "//p[contains(text(),'Model')]/../p[@class = 'unf-prop-list-prop']/text()")[2].get()).replace(" ", "", 1)

        tempOS = str(response.xpath(
            "//p[contains(text(),'İşletim Sistemi')]/../p[@class = 'unf-prop-list-prop']/text()").get()).replace(" ", "", 1)
        if tempOS.__contains__("Windows"):
            notebookItem['operatingSystem'] = "Windows"
        elif tempOS.__contains__("Macos"):
            notebookItem['operatingSystem'] = "MacOS"
        else:
            notebookItem['operatingSystem'] = "FreeDOS"

        notebookItem['islemciTipi'] = str(response.xpath(
            "//p[contains(text(),'İşlemci')]/../p[@class = 'unf-prop-list-prop']/text()").get()).replace(" ", "", 1)
        notebookItem['islemciModeli'] = str(response.xpath("//p[contains(text(),'İşlemci Modeli')]/../p[@class = 'unf-prop-list-prop']/text()").get()).replace(" ", "", 1)
        notebookItem['ram'] = str(response.xpath("//p[contains(text(),'Bellek Kapasitesi')]/../p[@class = 'unf-prop-list-prop']/text()").get()).replace(" ", "", 1).replace(" GB", "")
        notebookItem['diskBoyutu'] = str(response.xpath("//p[contains(text(),'Disk Kapasitesi')]/../p[@class = 'unf-prop-list-prop']/text()").get()).replace(" ", "", 1).replace(" GB", "").replace(" TB", "")

        tempType = str(response.xpath("//p[contains(text(),'Disk Türü')]/../p[@class = 'unf-prop-list-prop']/text()").get()).replace(" ", "", 1)

        if tempType.__contains__("SSD"):
            notebookItem['diskTuru'] = "SSD"
        elif tempType.__contains__("HDD"):
            notebookItem['diskTuru'] = "HDD"


        notebookItem['ekranBoyutu'] = str(response.xpath("//p[contains(text(),'Ekran Boyutu')]/../p[@class = 'unf-prop-list-prop']/text()").get()).replace(" ", "", 1).replace("\"", "")
        notebookItem['ekranKarti'] = str(response.xpath("//p[contains(text(),'Ekran Kartı Modeli')]/../p[@class = 'unf-prop-list-prop']/text()").get()).replace(" ", "", 1)

        linkImage = response.css("div.imgObj > a")
        notebookItem["image"] = linkImage.xpath('.//@href').get()

        if self.dbmanager.count_documents({"model": notebookItem['model'], }) == 0:
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
                "n11Fiyat": notebookItem['fiyat'],
                "n11": True,
                "n11Url": notebookItem['url'],
                "image": notebookItem['image']
            })
        else:
            self.dbmanager.update_one({"model": notebookItem['model'],
                                       }, {"$set": {
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
                "n11Fiyat": notebookItem['fiyat'],
                "n11": True,
                "n11Url": notebookItem['url'],
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
