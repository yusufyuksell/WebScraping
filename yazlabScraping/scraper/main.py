from scraper.scraper.spiders.n11 import N11Spider
from scraper.scraper.spiders.vatan import VatanSpider
from scraper.scraper.spiders.incehesap import IncehesapSpider
from scrapy.crawler import CrawlerProcess

def crawlAll():
    
    n11 = CrawlerProcess()
    n11.crawl(N11Spider)
    n11.start()

    vatan = CrawlerProcess()
    vatan.crawl(VatanSpider)
    vatan.start()
    
    incehesap = CrawlerProcess()
    incehesap.crawl(IncehesapSpider)
    incehesap.start()


if __name__ == '__main__':
    crawlAll()

