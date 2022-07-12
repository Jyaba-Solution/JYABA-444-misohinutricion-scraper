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
            products = response.xpath("//div[@class='category-products']/ul/li/a/@href").extract()
            for product in products:
                yield scrapy.Request(product, callback=self.parse_product)

        next_page = response.xpath("//div[@class='pages']/ol/li/a[contains(@class,'i-next')]/@href").extract_first()
        categories_list = response.xpath("//div[contains(@class,'categories-list')]//li//a/@href").extract()
        see_all_products = response.xpath("//div[contains(@class,'see-all')]/a/@href").extract()

        # check if it's product page
        product_name = response.xpath('//div[@class="product-name"]').extract_first()
        if next_page:
            open('next_page.txt', 'a').write(next_page + '\n')
            yield scrapy.Request(next_page, callback=self.parse_page)
        elif product_list:
            self.logger.info("Skipped page %s", response.url)
        elif categories_list:
            # checking the categories_list 
            categories_list = response.xpath("//div[contains(@class,'categories-list')]//li//a/@href").extract()
            if categories_list:
                for category in categories_list:
                    yield scrapy.Request(category, callback=self.parse_page)

        elif product_name:
            # we need to either yeild here or again parse the call
            yield scrapy.Request(response.url, callback=self.parse_product)
        elif see_all_products:
            # we need to either yeild here or again parse the call
            for product in see_all_products:
                yield scrapy.Request(product, callback=self.parse_page)
        else:
            self.logger.info(f'No more pages to crawl for {response.url}')
            open('crawled_urls.txt', 'a').write(response.url + '\n')

        # TODO find the next page


    
    def parse_product(self, response):
        breakpoint()
        product_name = response.xpath("//div[@class='product-name']/h1/text()").extract_first()
        brand_name = response.xpath("//*[@itemprop='brand']/text()").extract_first()
        format = ''
        normal_price = ''
        discounted_price = ''
        product_image_url = ''
        yield {
            'url': response.url,
            'name': response.xpath("//div[@class='product-name']/h1/text()").extract_first(),
        }
