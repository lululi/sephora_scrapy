from items import ReviewItem
from lxml import html
from scrapy import Spider, Request
import json
import math
import os
import pandas as pd
import re
import time


n_count_tot = 0
product_count_tot = 0

SOURCE_FILE_PATH = '/Users/cyl/Desktop/dermstore/'
REVIEW_PAGE_SIZE = 1000

class DermStoreSpider(Spider):
    name = "dermstore_spider"

    # a placeholder url to start the spider
    start_urls = ["https://www.google.com"]

    def parse(self, response):
        #time.sleep(0.5)

        # open a list of html files from disk
        counter = 0
        for filename in os.listdir(SOURCE_FILE_PATH):
            if counter > 0:
                break
            counter += 1

            print("*"*50)
            print(filename)
            print("*"*50)
            with open(SOURCE_FILE_PATH+filename, "r") as f:
                # load html file into parsable object
                page = f.read()
                tree = html.fromstring(page)

                # get category from file name
                category = os.path.splitext(filename)[0].split('-', 1)[0].lower()

                # extract values for each attribute
                product_ids = tree.xpath('//div[@data-product-id]//meta[@itemprop="mpn"]//@content')
                product_categories = [category for n in range(len(product_ids))]
                product_urls = tree.xpath('//div[@data-product-id]//meta[@itemprop="url"]//@content')
                product_names = [name.rstrip().lstrip() for name in tree.xpath('//div[@data-product-id]//p[@itemprop="name"]/text()')]
                brand_names = tree.xpath('//div[@data-product-id]//a[@itemprop="brand"]/text()')
                product_prices = tree.xpath('//div[@data-product-id]//meta[@itemprop="price"]//@content')
                product_stars = tree.xpath('//div[@data-product-id]//meta[@itemprop="ratingValue"]//@content')
                # not all product has review, so the array lenth dim could be different from others. 
                # review_counts = tree.xpath('//div[@data-product-id]//meta[@itemprop="reviewCount"]//@content')
                product_images_sm = ["https:" + url for url in tree.xpath('//div[@data-product-id]//img[@itemprop="image"]//@src')]
                product_images_lg = [("https:" + url).replace("300x300", "800x800") for url in tree.xpath('//div[@data-product-id]//img[@itemprop="image"]//@src')]

                # merge lists together
                product_df = pd.DataFrame({'p_id': product_ids, 'brand_name': brand_names, 'product': product_names,
                    'p_star': product_stars, 'p_categories': product_categories, 'p_price': product_prices,
                    'p_hero_image': product_images_sm, 'p_large_image': product_images_lg, 'p_product_url': product_urls})


                # crawl individual product review api
                for n in list(product_df.index):
                    if n>0:
                        time.sleep(3)

                    # if n>0:
                    #     break

                    product = product_df.loc[n, 'product']
                    p_id = product_df.loc[n, 'p_id']
                    p_star = product_df.loc[n, 'p_star']
                    p_brand = product_df.loc[n, 'brand_name']
                    p_price = product_df.loc[n, 'p_price']
                    p_category = product_df.loc[n, 'p_categories']
                    p_hero_image = product_df.loc[n, 'p_hero_image']
                    p_large_image = product_df.loc[n, 'p_large_image']
                    p_product_url = product_df.loc[n, 'p_product_url']

                    # construct product review link from p_id
                    link = "https://www.dermstore.com/ajax/review_list.php?prod_id={}" \
                    "&ipp={}&layout=dolphin&page=1&review_list_filter_type=skin&sort=".format(p_id, 1)

                    yield Request(link, callback=self.parse_page,
                                  meta={'product': product,'p_id':p_id, 'p_star':p_star, 'p_brand':p_brand,
                                        'p_price': p_price, 'p_category': p_category, 'p_hero_image': p_hero_image,
                                        'p_large_image': p_large_image, 'p_url': p_product_url})
                # print("*"*50)
                # print("total product number in this file {}".format(n))
                # print("*"*50)


    def parse_page(self, response):
        # check pagination, get total review number
        pages = response.xpath('//div[@class="pagination"]//a/text()').getall()

        if pages and pages[-1] == 'next':
            max_page = int(pages[-2])

            # paginated review api call for current product
            link = "https://www.dermstore.com/ajax/review_list.php?prod_id={}" \
                   "&ipp={}&layout=dolphin&page=1&review_list_filter_type=skin&sort=".format(response.meta['p_id'], max_page)

            # sleep a bit to prevent being blocked by server
            time.sleep(5)

            print("*"*50)
            print("start crawling total review url " + link)
            print("*"*50)

            yield Request(link, callback=self.parse_review,
                          meta={'product': response.meta['product'],'p_id':response.meta['p_id'], 
                                'p_star':response.meta['p_star'], 'p_brand':response.meta['p_brand'],
                                'p_price': response.meta['p_price'], 'p_category': response.meta['p_category'], 
                                'p_hero_image': response.meta['p_hero_image'], 'p_large_image': response.meta['p_large_image'], 
                                'p_url': response.meta['p_url'],
                                'p_num_reviews': max_page})


    def parse_review(self, response):
        print("*"*50)
        print("parsing review from " + link)
        print("*"*50)
        product = response.meta['product']
        p_id = response.meta['p_id']
        p_star = response.meta['p_star']
        p_brand = response.meta['p_brand']
        p_price = response.meta['p_price']
        p_category = response.meta['p_category']
        p_num_reviews = response.meta['p_num_reviews']
        p_image = response.meta['p_hero_image']
        p_image_lg = response.meta['p_large_image']
        p_url = response.meta['p_url']

        # get a list of reviews
        reviews = response.xpath('//div[@class="panel panel-default"]')

        for review in reviews:    
            # parse review related data
            reviewer_info_1 = review.xpath('div[@class="row"]//div[@class="col-sm-3 reviewer"]//p[position()=1]//text()').getall()
            reviewer_info_2 = review.xpath('div[@class="row"]//div[@class="col-sm-3 reviewer"]//p[position()=2]//text()').getall()
            review_star = review.xpath('div[@class="row"]//div[@class="col-sm-9"]//div/@class').get()[13:]
            review_title = review.xpath('div[@class="row"]//div[@class="col-sm-9"]//h5/text()').get().rstrip().lstrip()
            review_content = review.xpath('div[@class="row"]//div[@class="col-sm-9"]//p/text()').get().rstrip().lstrip()

            if len(reviewer_info_1) > 0:
                gender = None
                skin_type = None
                skin_tone = None
                age = None

                # gender
                if 'Female' in reviewer_info_1:
                    gender = 'Female'
                elif 'Male' in reviewer_info_1:
                    gender = 'Male'

                # skin type
                if 'Skin Type: ' in reviewer_info_1:
                    idx = reviewer_info_1.index('Skin Type: ') + 1
                    if idx < len(reviewer_info_1):
                        skin_type = reviewer_info_1[reviewer_info_1.index('Skin Type: ') + 1]

                # skin tune
                if 'Skin Tone: ' in reviewer_info_1:
                    idx = reviewer_info_1.index('Skin Tone: ') + 1
                    if idx < len(reviewer_info_1):
                        skin_tone = reviewer_info_1[reviewer_info_1.index('Skin Tone: ') + 1]

                # age
                if 'Age: ' in reviewer_info_1:
                    idx = reviewer_info_1.index('Age: ') + 1
                    if idx < len(reviewer_info_1):
                        age = reviewer_info_1[reviewer_info_1.index('Age: ') + 1]

            if len(reviewer_info_2) > 0:
                # date
                review_date = reviewer_info_2[-1].rstrip().lstrip()

                # location
                location = None
                for idx, val in enumerate(reviewer_info_2):
                    trimed_val = val.rstrip().lstrip()
                    if trimed_val.startswith('from'):
                        location = trimed_val[5:]

                # reviewer name
                first = reviewer_info_2[0].rstrip().lstrip()
                reviewer = None
                if not first.startswith('from') and not first.startswith('Verified') and not re.match("\d+/\d+/\d+", first):
                    reviewer = first

            item = ReviewItem()
            item['product'] = product
            item['p_id'] = p_id
            item['p_star'] = p_star
            item['brand_name'] = p_brand
            item['p_price'] = p_price
            item['p_categories'] = p_category
            item['p_num_reviews'] = p_num_reviews 
            item['p_product_url'] = p_url
            item['p_hero_image'] = p_image
            item['p_large_image'] = p_image_lg

            item['reviewer'] = reviewer
            item['r_star'] = review_star
            item['r_skintone'] = skin_tone
            item['r_skintype'] = skin_type
            item['r_review'] = review_content
            item['r_last_modified_time'] = review_date
            item['r_userlocation'] = location
            item['r_title'] = review_title
            item['r_age'] = age
            item['r_gender'] = gender

            print(item['r_title'])
