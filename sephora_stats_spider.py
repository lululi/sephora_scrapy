from scrapy import Spider, Request, signals
from items import ReviewItem
import re
import pandas as pd
import json
import math
import time

n_count_tot = 0
product_count_tot = 0
skin_types = ["oily", "combination", "dry", "normal"]
stats = {}


class SephoraSpider(Spider):
    name = "sephora_spider"
    allowed_urls = ["https://www.sephora.com", "https://api.bazaarvoice.com"]
    start_urls = ["https://www.sephora.com"]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SephoraSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        spider.logger.info('Spider closed: %s', spider.name)
        with open('stats.txt', 'w') as outfile:
            json.dump(stats, outfile)

    def parse(self, response):
        # time.sleep(0.5)
        # category_links = ["/shop/moisturizing-cream-oils-mists", "/shop/cleanser", "shop/facial-treatments",
        #                   "/shop/eye-treatment-dark-circle-treatment", "/shop/face-mask",
        #                   "/shop/sunscreen-sun-protection", "/shop/lip-treatments"]
        category_links = ["/shop/face-serum"]

        # this scrapes only the brands inside brand_links
        links = ["https://www.sephora.com" + link for link in category_links]

        for url in links:
            # time.sleep(0.5)
            yield Request(url, callback=self.parse_page, meta={'url': url})

    def parse_page(self, response):
        num_products = int(response.xpath('//span[@data-at="number_of_products"]/text()').extract_first()[:-9])
        max_page = math.ceil(num_products / 300)
        base_url = response.meta['url']
        links = [base_url + '?pageSize=300&currentPage={}'.format(x + 1) for x in range(max_page)]
        for url in links:
            yield Request(url, callback=self.parse_product, meta={'url': url})

    def parse_product(self, response):
        # time.sleep(0.5)
        data = response.xpath('//script[@id="linkJSON"]/text()').extract_first()
        dictionary = json.loads(data)
        catalog = None
        for entry in dictionary:
            if entry['class'] == 'CatalogPage':
                catalog = entry['props']['products']
        if catalog == None:
            return
        product_urls = [x['targetUrl'] for x in catalog]
        product_names = [x['displayName'] for x in catalog]
        product_ids = [x['productId'] for x in catalog]
        ratings = [x['rating'] for x in catalog]
        brand_names = [x['brandName'] for x in catalog]
        image_urls = ["https://www.sephora.com/" + x['image250'] for x in catalog]

        links2 = ["https://www.sephora.com" + link for link in product_urls]

        global product_count_tot
        product_count_tot += len(links2)

        try:
            product_df = pd.DataFrame({'links2': links2, 'product_names': product_names, 'p_id': product_ids,
                                       'ratings': ratings, 'brand_names': brand_names, 'image_urls': image_urls})
        except:
            print('=' * 50)
            print('Number of products do not match with ratings')
            print('currentURL::::::::' + response.meta['url'])
            print("urls::::::::{}".format(len(product_urls)))
            print("ratings:::::{}".format(len(ratings)))
            print("brands::::::{}".format(len(brand_names)))
            print("products::::{}".format(len(product_names)))
            print("ids:::::::::{}".format(len(product_ids)))
            print("images::::::{}".format(len(image_urls)))
            print('=' * 50)
            return

        print(product_df.head())
        print(list(product_df.index))

        for n in list(product_df.index):
            product = product_df.loc[n, 'product_names']
            p_id = product_df.loc[n, 'p_id']
            p_star = product_df.loc[n, 'ratings']
            brand_name = product_df.loc[n, 'brand_names']
            p_hero_image = product_df.loc[n, 'image_urls']

            print(product_df.loc[n, 'links2'])

            if n > 0:
                time.sleep(1)

            yield Request(product_df.loc[n, 'links2'], callback=self.parse_detail,
                          meta={'product': product, 'p_id': p_id, 'p_star': p_star, 'brand_name': brand_name,
                                'p_product_url': product_df.loc[n, 'links2'], 'p_hero_image': p_hero_image})

    def parse_detail(self, response):
        # time.sleep(0.5)
        print('parse_detail')
        product = response.meta['product']
        p_id = response.meta['p_id']
        p_star = response.meta['p_star']
        brand_name = response.meta['brand_name']
        p_hero_image = response.meta['p_hero_image']
        p_product_url = response.meta['p_product_url']

        data = response.xpath('//script[@type="application/ld+json"]/text()').extract()
        dictionary = [json.loads(x) for x in data]
        p_category = None
        p_prices = []
        p_sizes = []
        for entry in dictionary:
            try:
                if entry['@type'] == 'BreadcumbList':
                    p_category = entry['itemListElement'][-1]['item']['name']
                if entry['@type'] == 'Product':
                    for offer in entry['offers']:
                        p_prices.append(offer['price'])
                    if 'additionalProperty' in entry:
                        for addition in entry['additionalProperty']:
                            if addition['name'] == 'size':
                                p_sizes.append(addition['value'])
                    else:
                        size_text = response.xpath('//span[count(@*)=0]/text()').extract()
                        if len(size_text) > 2 and size_text[0].strip() == 'SIZE':
                            p_sizes.append(size_text[1].strip())
            except:
                print("Error processing prices/sizes from following entry:::::")
                print(entry)
                print(p_sizes)

        review_link = 'https://api.bazaarvoice.com/data/reviews.json?Filter=ProductId%3A' + p_id + '&Sort=SubmissionTime%3Adesc&Limit=10&Offset=0&Include=Products%2CComments&Stats=Reviews&passkey=rwbw526r2e7spptqd2qzbkp7&apiversion=5.4'
        yield Request(review_link, callback=self.parse_review_count,
                      meta={'product': product, 'p_id': p_id, 'p_star': p_star, 'brand_name': brand_name,
                            'p_category': p_category, 'p_prices': p_prices, 'p_sizes': p_sizes,
                            'p_hero_image': p_hero_image, 'p_product_url': p_product_url})

    def parse_review_count(self, response):
        data = json.loads(response.text)
        p_id = response.meta['p_id']
        p_num_reviews = data['TotalResults']
        print('Number of reviews: {}'.format(p_num_reviews))

        # create code here that creates a list of urls for calling the reviews
        # you will use p_num_reviews, use the "{}".format technique

        max_n = math.ceil(p_num_reviews / 100)
        # low_range = [x*30 for x in list(range(0,max_n))]
        # up_range = [x*30 for x in list(range(1,max_n+1))]

        links3 = ['https://api.bazaarvoice.com/data/reviews.json?Filter=ProductId%3A' +
                  p_id + '&Sort=SubmissionTime%3Adesc&Limit=' +
                  '100&Offset={}&Include=Products%2CComments&'.format(x) +
                  'Stats=Reviews&passkey=rwbw526r2e7spptqd2qzbkp7&apiversion=5.4' for x in range(max_n)]

        for url in links3:
            # time.sleep(0.5)
            yield Request(url, callback=self.parse_reviews,
                          meta={'product': response.meta['product'], 'p_id': response.meta['p_id'],
                                'p_star': response.meta['p_star'], 'brand_name': response.meta['brand_name'],
                                'p_category': response.meta['p_category'], 'p_num_reviews': p_num_reviews,
                                'p_prices': response.meta['p_prices'], 'p_sizes': response.meta['p_sizes'],
                                'p_hero_image': response.meta['p_hero_image'],
                                'p_product_url': response.meta['p_product_url']})

    def parse_reviews(self, response):
        # time.sleep(0.5)
        print('parse_reviews')

        product = response.meta['product']
        p_id = response.meta['p_id']
        p_star = response.meta['p_star']
        brand_name = response.meta['brand_name']
        p_prices = response.meta['p_prices']
        p_sizes = response.meta['p_sizes']
        p_category = response.meta['p_category']
        p_num_reviews = response.meta['p_num_reviews']
        p_hero_image = response.meta['p_hero_image']
        p_product_url = response.meta['p_product_url']

        data = json.loads(response.text)
        reviews = data['Results']  # this is a list
        # each element inside reviews is a dictionary
        # tmp[0].keys() will give the keys of the dictionaries inside reviews

        # create code here which arranges the data from the json dictionary into a dataframe

        n_count = 0
        global n_count_tot, product_count_tot, stats

        for review in reviews:
            try:
                reviewer = review['UserNickname']
            except:
                reviewer = None
            try:
                r_star = review['Rating']
            except:
                r_star = None

            try:
                r_eyecolor = review['ContextDataValues']['eyeColor']['Value']
            except:
                r_eyecolor = None

            try:
                r_haircolor = review['ContextDataValues']['hairColor']['Value']
            except:
                r_haircolor = None

            try:
                r_skintone = review['ContextDataValues']['skinTone']['Value']
            except:
                r_skintone = None

            try:
                r_skintype = review['ContextDataValues']['skinType']['Value']
            except:
                r_skintype = None
            try:
                r_skinconcerns = review['ContextDataValues']['skinConcerns']['Value']
            except:
                r_skinconcerns = None

            try:
                r_review = review['ReviewText']
            except:
                r_review = None

            try:
                r_last_modified_time = review['LastModificationTime']
            except:
                r_last_modified_time = None

            try:
                r_negative_count = review['TotalNegativeFeedbackCount']
            except:
                r_negative_count = None

            try:
                r_positive_count = review['TotalPositiveFeedbackCount']
            except:
                r_positive_count = None

            try:
                r_userlocation = review['UserLocation']
            except:
                r_userlocation = None

            try:
                r_title = review['Title']
            except:
                r_title = None

            # time.sleep(0.025)
            n_count += 1
            n_count_tot += 1

            if r_skintype:
                if p_id not in stats:
                    stats[p_id] = {}
                    stats[p_id]['brand_name'] = brand_name
                    stats[p_id]['product_name'] = product
                    for t in skin_types:
                        stats[p_id][t] = {}
                        stats[p_id][t]['score_sum'] = 0
                        stats[p_id][t]['review_sum'] = 0
                stats[p_id][r_skintype]['score_sum'] += r_star
                stats[p_id][r_skintype]['review_sum'] += 1

        # time.sleep(20)
        print('='*50)
        print(stats[p_id])
        print('='*50)
        # time.sleep(10)
