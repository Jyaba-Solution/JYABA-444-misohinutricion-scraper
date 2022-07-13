import scrapy

# https://www.misohinutricion.com/synerviol-nutergia.html
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
            if response.meta.get('next_page_checker', False):
                with open('next_page_urls.txt', 'a') as f:
                    f.write(response.url + '\n')
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
            yield scrapy.Request(next_page, callback=self.parse_page, dont_filter=True, meta={'next_page_checker': True})
        elif product_list:
            self.logger.info("Skipped page %s", response.url)
            with open('skipped_pages.txt', 'a') as f:
                f.write(response.url + '\n')
        elif categories_list:
            # checking the categories_list 
            categories_list = response.xpath("//div[contains(@class,'categories-list')]//li//a/@href").extract()
            if categories_list:
                for category in categories_list:
                    yield scrapy.Request(category, callback=self.parse_page)

        elif product_name:
            # we need to either yeild here or again parse the call
            yield scrapy.Request(response.url, callback=self.parse_product, dont_filter=True)
        elif see_all_products:
            # we need to either yeild here or again parse the call
            for product in see_all_products:
                yield scrapy.Request(product, callback=self.parse_page)
        else:
            self.logger.info(f'No more pages to crawl for {response.url}')
            open('crawled_urls.txt', 'a').write(response.url + '\n')

        # TODO find the next page

    def extract_number(self, text):
        try:
            return float(text.replace(',', '.'))
        except Exception as e:
            return 0
    
    def parse_product(self, response):
        try:
            product_name = response.xpath("//div[@class='product-name']/h1/text()").extract_first()
            brand_name = response.xpath("//*[@itemprop='brand']/text()").extract_first()
            description_text = response.xpath('//div[@id="product_tabs_description_contents"]//text()').extract()
            composition_text = response.xpath('//div[@id="product_tabs_composicion_contents"]//text()').extract()
            daily_dosie_text = response.xpath('//div[@id="product_tabs_dosis_contents"]//text()').extract()
            observations_text = response.xpath('//div[@id="product_tabs_observations_contents"]//text()').extract()
            brand_text = response.xpath('//div[@id="brandaboutcontent"]//text()').extract()
            brand_id = response.xpath('//div[@id="brandaboutcontent"]/@class').extract_first()
            img = response.css('.prolabel-wrapper img::attr("src")').extract_first()

            # https://www.misohinutricion.com/misohi/index/brand/id/63
            formats_element = response.xpath("//div[@class='conf-options np-1']")
            for format_element in formats_element:
                format_name = format_element.xpath("//div[@class='conf-option np-1']//div[@class='product-presentation']//text()").extract()
                old_price = format_element.xpath(".//div[@itemprop='offers']/div[@class='price-box']/p[@class='old-price']/span[@class='price']//text()").extract_first()
                sale_price = response.xpath('//meta[@itemprop="price"]/@content').extract_first()
                yield {
                    'product_name': product_name,
                    'brand_name': brand_name,
                    'description_text': description_text,
                    'composition_text': composition_text,
                    'daily_dosie_text': daily_dosie_text,
                    'observations_text': observations_text,
                    'brand_text': brand_text,
                    'brand_id': brand_id,
                    'img': img,
                    'format_name': ' '.join(format_name).strip() if format_name else '',
                    'old_price': ''.join(old_price).strip() if old_price else None,
                    'sale_price': sale_price,
                    'url': response.url
                }
        except Exception as e:
            self.logger.info(f'Error parsing {response.url}')
            self.logger.info(e)
            open('error_urls.txt', 'a').write(response.url + '\n')
            breakpoint()