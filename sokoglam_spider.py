from scrapy import Spider, Request
from items import ReviewItem
import re
import pandas as pd
import json
import math
import time

n_count_tot = 0
product_count_tot = 0

class SokoglamSpider(Spider):

    name = "sokoglam_spider"
    allowed_urls = ["https://sokoglam.com", "https://api.yotpo.com"]
    start_urls = ["https://sokoglam.com/collections/skincare"]

    #first is to collect all the links for all the pages
    def parse(self, response):
        #time.sleep(0.5)
        product_ids = response.xpath('//div[has-class("product-grid-item")]/@data-id').extract()
        product_names = response.xpath('//div[has-class("product-grid-item")]/@data-name').extract()
        product_urls = response.xpath('//div[@class="yotpo bottomLine"]/@data-url').extract()
        image_urls = ['https:' + re.sub(r'%3Fv=\d+', '', x) for x in response.xpath('//div[@class="yotpo bottomLine"]/@data-image-url').extract()]
        list_prices = response.xpath('//span[@class="ProductPrice"]/text()').extract()
        product_brands = response.xpath('//span[@class="product__vendor"]/a/text()').extract()
        global product_count_tot
        product_count_tot += len(product_urls)

        product_df = pd.DataFrame({'product_urls': product_urls,'product_names': product_names,'p_id': product_ids, 
                                   'p_image': image_urls, 'p_price': list_prices, 'p_brand': product_brands})
        print (product_df.head())
        print (list(product_df.index))

        for n in list(product_df.index):
            product = product_df.loc[n, 'product_names']
            p_id = product_df.loc[n, 'p_id']
            p_price = product_df.loc[n, 'p_price']
            p_image = product_df.loc[n, 'p_image']
            p_brand = product_df.loc[n, 'p_brand']
            
            print ('{}::: {}'.format(n, product_df.loc[n, 'product_urls']))

            yield Request(product_df.loc[n, 'product_urls'], callback=self.parse_detail,
                          meta = {'product': product, 'p_id': p_id, 'p_brand': p_brand,
                                  'p_price': p_price, 'p_url': product_df.loc[n, 'product_urls'],
                                  'p_image': p_image})
            
    def parse_detail(self, response):
        time.sleep(1)
        product = response.meta['product']
        p_id = response.meta['p_id']
        p_category = re.findall('"type":"(.*?)",', response.xpath('//script[contains(text(), "var meta = {")]/text()').extract_first())
        p_price = response.meta['p_price']
        p_url = response.meta['p_url']
        p_image = response.meta['p_image']
        p_brand = response.meta['p_brand']
        try:
            p_star = float(response.xpath('//span[@itemprop="ratingValue"]/text()').extract_first())
        except:
            p_star = None
        try:
            p_num_reviews = int(response.xpath('//span[@itemprop="ratingCount"]/text()').extract_first())
        except:
            p_num_reviews = 0

        if p_num_reviews == 0:
            return

        max_page = math.ceil(p_num_reviews/150)

        review_links = ['https://api.yotpo.com/v1/widget/kILjLgKH3AFJKWu0W8HoD8nuvs72obqsSPmWjHiG/products/' +
                        p_id + '/reviews.json?per_page=150&page={}'.format(x) for x in range(1, max_page + 1)]
        time.sleep(1)
        for url in review_links:
            yield Request(url, callback=self.parse_review,
                          meta={'product': product, 'p_id': p_id, 'p_star': p_star, 'p_brand': p_brand,
                                'p_category':p_category, 'p_num_reviews':p_num_reviews, 'p_price':p_price,
                                'p_image':p_image, 'p_url': p_url})

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

        data = json.loads(response.text)
        reviews = data['response']['reviews']

        n_count = 0
        global n_count_tot, product_count_tot
        for review in reviews:
            try:
                reviewer = review['user']['display_name']
            except:
                reviewr = None
            try:
                r_star = review['score']
            except:
                r_star = None
            try:
                r_skintype = review['custom_fields']['--2491']['value']
            except:
                r_skintype = None
            try:
                r_last_modified_time = review['created_at']
            except:
                r_last_modified_time = None
            try:
                r_positive_count = review['votes_up']
            except:
                r_positive_count = None
            try:
                r_negative_count = review['votes_down']
            except:
                r_negative_count = None
            try:
                r_title = review['title']
            except:
                r_title = None
            try:
                r_review = review['content']
            except:
                r_review = None

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

        #all of these needs to be taken from the reviews list/dictionary

            item['reviewer'] = reviewer
            item['r_star'] = r_star
            item['r_skintype'] = r_skintype
            item['r_review'] = r_review
            item['r_last_modified_time'] = r_last_modified_time
            item['r_negative_count'] = r_negative_count
            item['r_positive_count'] = r_positive_count
            item['r_title'] = r_title

            n_count += 1
            n_count_tot += 1
            yield item
            
        print ('='*50)
        print ('BRAND: {} PRODUCT: {}'.format(p_brand, product))
        print ('TOTAL NUMBER OF REVIEWS: {}'.format(int(p_num_reviews)))
        print ('TOTAL NUMBER PULLED FOR PRODUCT: {}'.format(len(reviews)))
        print ('ACTUAL NUMBER PULLED {}'.format(n_count))
        print ('TOTAL NUMBER PULLED {}'.format(n_count_tot))
        print ('TOTAL NUMBER PRODUCTS {}'.format(product_count_tot))
        print ('='*50)
        time.sleep(10)


