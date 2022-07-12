import scrapy


class MisohinutricionSpiderSpider(scrapy.Spider):
    name = 'misohinutricion'
    allowed_domains = ['misohinutricion.com']
    start_urls = ['https://www.misohinutricion.com']

    def parse(self, response):
        urls = [x for x in response.xpath('//a/@href').extract() if x.startswith('https://www.misohinutricion.com')]
        for url in urls:
            if not url.startswith('https://www.misohinutricion.com'):
                url = 'https://www.misohinutricion.com' + url
            yield scrapy.Request(url, callback=self.parse_page)
    
    def parse_page(self, response):
        product_list = response.xpath("//div[@class='category-products']")
        if product_list:
            products = response.xpath("//div[@class='category-products']/ul/li/a/@href")
            for product in products:
                yield scrapy.Request(product.extract(), callback=self.parse_product)

        next_page = response.xpath("//div[@class='pages']/ul/li/a[@title='Next']/@href")
        breakpoint()
