import scrapy

class LookfSpider(scrapy.Spider):
    name = "lookf"
    allowed_domains = ["www.lookfantastic.fr"]

    def start_requests(self):
        # List of URLs to start from
        start_urls = [
            {"url": "https://www.lookfantastic.fr/health-beauty/face/skincare-products.list", "category": "Soin Visage"},
            {"url": "https://www.lookfantastic.fr/health-beauty/make-up/view-all-make-up.list", "category": "Maquillage"},
            {"url": "https://www.lookfantastic.fr/health-beauty/hair/view-all-haircare.list", "category": "Soin Cheveux"},
            {"url": "https://www.lookfantastic.fr/health-beauty/parfum/voir-tout.list", "category": "Parfums"},
            {"url": "https://www.lookfantastic.fr/health-beauty/body/view-all-bodycare.list", "category": "Soin Corps"},
        ]

        for entry in start_urls:
            yield scrapy.Request(entry["url"], callback=self.parse, meta={'category': entry["category"]})

    def parse(self, response):
        # Extract product links from the current page
        product_links = response.css('a.productBlock_link::attr(href)').getall()

        # Print the extracted links
        for product_link in product_links:
            absolute_url = response.urljoin(product_link)
            yield scrapy.Request(absolute_url, callback=self.parse_product, meta={'category': response.meta['category']})

        # Follow pagination links
        total_pages = self.extract_total_pages(response)
        if total_pages:
            for page_number in range(2, total_pages + 1):
                page_url = response.urljoin(f'?pageNumber={page_number}')
                yield scrapy.Request(page_url, callback=self.parse, meta={'category': response.meta['category']})

    def extract_total_pages(self, response):
        # Extract the total number of pages from the current page
        # Modify this logic based on how the total number of pages is presented on the website
        total_pages = int(response.css('.responsivePaginationButton.responsivePageSelector.responsivePaginationButton--last::text').get().strip().replace('\n', ''))
        return int(total_pages) if total_pages else None

    def parse_product(self, response):
        # Extract additional information from the product page
        product_name = response.css('.productName h1::text').extract()
        product_price = str(response.css('div.productPrice p.productPrice_price ::text').extract()
                            [0]).strip().replace('\n', '')

        product_description = ''.join(response.css('#product-description-content-lg-2 p::text').extract())
        product_usage_guidelines = ''.join(response.css('#product-description-content-lg-15 p::text').extract())
        product_ingredients = ''.join(response.css('#product-description-content-lg-7 p::text').extract())
        product_brand = response.css(
            '.productDescription_contentWrapper ul[data-information-component="brand"] li.productDescription_contentPropertyValue_value::text').get()

        category = response.meta['category']

        # Process or store the extracted information as needed, including the 'category' information
        yield {
            'category': category,
            'product_name': product_name,
            'product_price': product_price,
            'product_description': product_description,
            'product_usage_guidelines': product_usage_guidelines,
            'product_ingredients': product_ingredients,
            'product_brand': product_brand
        }
