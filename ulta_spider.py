from scrapy import Spider, Request
from lxml import html
from items import ReviewItem
import re
import pandas as pd
import json
import math
import time

n_count_tot = 0
product_count_tot = 0

class ULTASpider(Spider):

    name = "ulta_spider"
    allowed_urls = ["https://www.ulta.com", "http://readservices-b2c.powerreviews.com"]
    start_urls = ["https://www.ulta.com"]

    def parse(self, response):
        #time.sleep(0.5)
        category_links = ["/skin-care-treatment-serums?N=27cs",]
        # category_links = ["/skin-care-cleansers?N=2794", "/skin-care-moisturizers?N=2796",
        #                   "/skin-care-treatment-serums?N=27cs",
        #                   "/skin-care-eye-treatments?N=270k", "/skin-care-suncare?N=27fe"]

        links = ["https://www.ulta.com" + link for link in category_links]

        for url in links:
            #time.sleep(0.5)
            yield Request(url, callback = self.parse_page, meta = {'current_url': url})

    def parse_page(self, response):
        max_page = int(response.xpath('//span[@class="upper-limit"]/text()').extract_first()[3:])

        base_url = response.meta['current_url'] 
        for x in range(max_page):
            url = base_url + "&No={}&Nrpp=96".format(96 * (x-1))
            yield Request(url, callback = self.parse_product, meta = {'url': url})
        
    def parse_product(self, response):
        product_ids = response.xpath('//div[@class="productQvContainer"]/@id').extract()

        product_urls = response.xpath('//a[@class="product"]/@href').extract()
        product_urls = ['https://www.ulta.com' + x for x in product_urls]
        
        product_brands = response.xpath('//h4[@class="prod-title"]//a/text()').extract()
        product_brands = [x.strip() for x in product_brands]

        product_names = response.xpath('//p[@class="prod-desc"]//a/text()').extract()
        product_names = [x.strip() for x in product_names]

        list_prices_raw = response.xpath('//div[@class="productPrice"]').extract()
        list_prices = []
        for x in list_prices_raw:
            html_x = html.fromstring(x)
            if len(html_x.xpath('//span[@class="regPrice"]/text()')) == 0:
                list_prices.append(html_x.xpath('//span[@class="pro-new-price"]/text()')[0].strip())
            else:
                list_prices.append(html_x.xpath('//span[@class="regPrice"]/text()')[0].strip())

        image_urls = [response.xpath('//img[@name="' + x + '"]/@src').extract() for x in product_ids]

        global product_count_tot
        product_count_tot += len(product_urls)

        try:
            product_df = pd.DataFrame({'product_urls': product_urls,'product_names': product_names,'p_id': product_ids, 
                                       'p_brand': product_brands, 'p_image': image_urls, 'p_price': list_prices})
        except:
            print ('='*50)
            print('Number of products do not match with ratings')
            print('currentURL::::::::' + response.meta['url'])
            print("urls::::::::{}".format(len(product_urls)))
            print("brands::::::{}".format(len(product_brands)))
            print("products::::{}".format(len(product_names)))
            print("ids:::::::::{}".format(len(product_ids)))
            print("images::::::{}".format(len(image_urls)))
            print("prices::::::{}".format(len(list_prices)))
            print ('='*50)
            return

        print (product_df.head())
        print (list(product_df.index))

        for n in list(product_df.index):
            product = product_df.loc[n, 'product_names']
            p_id = product_df.loc[n, 'p_id']
            p_brand = product_df.loc[n, 'p_brand']
            p_price = product_df.loc[n, 'p_price']
            p_image = product_df.loc[n, 'p_image']

            print ('{}::: {}'.format(n, product_df.loc[n, 'product_urls']))

            yield Request(product_df.loc[n, 'product_urls'], callback=self.parse_detail,
                          meta = {'product': product, 'p_id': p_id, 'p_brand': p_brand,
                                  'p_price': p_price, 'p_url': product_df.loc[n, 'product_urls'],
                                  'p_image': p_image})

    def parse_detail(self, response):
        product = response.meta['product']
        p_id = response.meta['p_id']
        p_brand = response.meta['p_brand']
        p_price = response.meta['p_price']
        p_url = response.meta['p_url']
        p_image = response.meta['p_image']

        dictionary = response.xpath('//script[@type="application/ld+json"]/text()').extract()
        product_dict = json.loads(dictionary[0])
        category_dict = json.loads(dictionary[1])
        
        p_category = category_dict['itemListElement'][-2]['item']['name']
        # ULTA has cleansing brushes under cleansers, we don't need tools for now
        if p_category == 'Cleansing Brushes':
            return
        p_star = product_dict['aggregateRating']['ratingValue']
        p_num_reviews = product_dict['aggregateRating']['reviewCount']

        max_page = math.ceil(p_num_reviews / 25)

        review_links = ['http://readservices-b2c.powerreviews.com/m/6406/l/en_US/product/' +
                        p_id + '/reviews?apikey=daa0f241-c242-4483-afb7-4449942d1a2b' +
                        '&paging.size=25&paging.from={}'.format(x * 25) for x in range(max_page)]

        for url in review_links:
            yield Request(url, callback=self.parse_review,
                          meta={'product': product, 'p_id': p_id, 'p_star': p_star, 'p_brand': p_brand,
                                'p_category':p_category, 'p_num_reviews':p_num_reviews, 'p_price':p_price,
                                'p_image':p_image, 'p_url': p_url, 'review_link': url})

    def parse_review(self, response):
        product = response.meta['product']
        p_id = response.meta['p_id']
        p_star = response.meta['p_star']
        p_brand = response.meta['p_brand']
        p_price = response.meta['p_price']
        p_category = response.meta['p_category']
        p_num_reviews = response.meta['p_num_reviews']
        p_image = response.meta['p_image']
        p_url = response.meta['p_url']
        review_link = response.meta['review_link']
        
        data = json.loads(response.text)
        n_count = 0
        global n_count_tot, product_count_tot
        for result in data['results']:
            reviews = result['reviews']
            for review in reviews:
                try:
                    reviewer = review['details']['nickname']
                except:
                    reviewr = None
                try:
                    r_star = review['metrics']['rating']
                except:
                    r_star = None
                try:
                    r_last_modified_time = review['details']['updated_date']
                except:
                    r_last_modified_time = None
                try:
                    r_positive_count = review['metrics']['helpful_votes']
                except:
                    r_positive_count = None
                try:
                    r_negative_count = review['metrics']['not_helpful_votes']
                except:
                    r_negative_count = None
                try:
                    r_title = review['details']['headline']
                except:
                    r_title = None
                try:
                    r_review = review['details']['comments']
                except:
                    r_review = None
                try:
                    r_userlocation = review['details']['location']
                except:
                    r_userlocation = None

                try:
                    r_skintype = None
                    for p in review['details']['properties']:
                        if p['key'] == 'describeyourself':
                            for v in p['value']:
                                if ('dry' or 'oily' or 'combination' or 'sensitive' or 'normal') in v.lower():
                                    r_skintype = v
                except:
                    r_skintype = None


                item = ReviewItem()
                item['product'] = product
                item['p_id'] = p_id
                item['p_star'] = p_star
                item['brand_name'] = p_brand
                item['p_prices'] = [p_price]
                item['p_category'] = p_category
                item['p_num_reviews'] = p_num_reviews 
                item['p_product_url'] = p_url
                item['p_hero_image'] = p_image

        #all     of these needs to be taken from the reviews list/dictionary

                item['reviewer'] = reviewer
                item['r_star'] = r_star
                item['r_skintype'] = r_skintype
                item['r_review'] = r_review
                item['r_last_modified_time'] = r_last_modified_time
                item['r_negative_count'] = r_negative_count
                item['r_positive_count'] = r_positive_count
                item['r_title'] = r_title
                item['r_userlocation'] = r_userlocation

                n_count += 1
                n_count_tot += 1
                yield item
            
        print ('='*50)
        print ('BRAND: {} PRODUCT: {}'.format(p_brand, product))
        print ('TOTAL NUMBER OF REVIEWS: {}'.format(int(p_num_reviews)))
        print ('REVIEW PULLING URL: {}'.format(review_link))
        print ('TOTAL NUMBER PULLED FOR PRODUCT: {}'.format(len(reviews)))
        print ('ACTUAL NUMBER PULLED {}'.format(n_count))
        print ('TOTAL NUMBER PULLED {}'.format(n_count_tot))
        print ('TOTAL NUMBER PRODUCTS {}'.format(product_count_tot))
        print ('='*50)
        time.sleep(10)



