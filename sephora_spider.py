from scrapy import Spider, Request
from items import SephoraItem
import re
import pandas as pd
import json
import math
import time

n_count_tot = 0
product_count_tot = 0

class SephoraSpider(Spider):

    name = "sephora_spider"
    allowed_urls = ["https://www.sephora.com", "https://api.bazaarvoice.com"]
    #start_urls = ["https://www.sephora.com/brand/list.jsp"]
    start_urls = ["https://www.sephora.com"]

    #first is to collect all the links for all the brands
    #but this will not be used because the data is just too much. I'll just define the links

    def parse(self, response):
        #time.sleep(0.5)
        #this scrapes all of the brands
        #links = response.xpath('//a[@class="u-hoverRed u-db u-p1"]//@href').extract()
        #links = [x + "?products=all" for x in links]
        
        #brand_links = ["/fenty-beauty-rihanna", "/kiehls", "/lancome", "/estee-lauder", "/the-ordinary",
        #"/shiseido", "/sk-ii", "/clinique", "/benefit-cosmetics", "dr-jart", "/chanel", "/nars",
        #"/laneige", "/urban-decay", "/bobbi-brown"]
        brand_links = ["/drunk-elephant"]
        brand_links = [x + "?products=all" for x in brand_links]

        #this scrapes only the brands inside brand_links
        links = ["https://www.sephora.com" + link for link in brand_links]

        for url in links:
            #time.sleep(0.5)
            yield Request(url, callback=self.parse_product)

    def parse_product(self, response):
        #time.sleep(0.5)
        dictionary = response.xpath('//script[@id="linkJSON"]').extract()
        dictionary = re.findall('"products":\[(.*?)\]', dictionary[0])[0]
        
        product_urls = re.findall('"targetUrl":"(.*?)",', dictionary)
        product_names = re.findall('"displayName":"(.*?)",', dictionary)
        product_ids = re.findall('"productId":"(.*?)",', dictionary)
        ratings = re.findall('"rating":(.*?),', dictionary)
        brand_names = re.findall('"brandName":"(.*?)",', dictionary)
        list_prices = re.findall('"listPrice":(.*?),', dictionary)
        # sale_prices

        links2 = ["https://www.sephora.com" + link for link in product_urls]
        if len(product_urls)!=len(ratings)!=len(brand_names):
            print('Number of products do not match with ratings')

        global product_count_tot
        product_count_tot = len(links2)

        product_df = pd.DataFrame({'links2': links2,'product_names': product_names,'p_id': product_ids, 
            'ratings': ratings,'brand_names': brand_names, 'p_price': list_prices})

        print (product_df.head())
        print (list(product_df.index))

        for n in list(product_df.index):
            product = product_df.loc[n, 'product_names']
            p_id = product_df.loc[n, 'p_id']
            p_star = product_df.loc[n, 'ratings']
            brand_name = product_df.loc[n, 'brand_names']
            p_price = product_df.loc[n, 'p_price']

            print (product_df.loc[n,'links2'])

            if n>0:
                time.sleep(1)

            if p_id =='P419222':
                yield Request(product_df.loc[n,'links2'], callback=self.parse_detail,
                              meta={'product': product, 'p_id':p_id, 'p_star':p_star, 'brand_name':brand_name,
                                    'p_price': p_price, 'p_product_url': product_df.loc[n,'links2']})

    def parse_detail(self, response):
        #time.sleep(0.5)
        print ('parse_detail')

        product = response.meta['product']
        p_id = response.meta['p_id']
        p_star = response.meta['p_star']
        brand_name = response.meta['brand_name']
        p_price = response.meta['p_price']
        p_hero_image = "https://www.sephora.com/" + response.xpath('//meta[@property="og:image"]/@content').extract_first()
        p_product_url = response.meta['p_product_url']
        p_categories = response.xpath('//a[@class="css-1ylrown "]/text()').extract()
        p_categories += response.xpath('//h1[@class="css-bnsadm "]/text()').extract()

        p_num_reviews = response.xpath('//a[@data-comp="RatingsSummary Flex Box"]/span/text()').extract()
        p_num_reviews = p_num_reviews[0]
        p_num_reviews = p_num_reviews.replace('s', '')
        p_num_reviews = p_num_reviews.replace(' review', '')
        p_num_reviews = p_num_reviews.replace('K', '000')
        p_num_reviews = int(p_num_reviews)

        print ('Number of reviews: {}'.format(p_num_reviews))

        #create code here that creates a list of urls for calling the reviews
        #you will use p_num_reviews, use the "{}".format technique

        max_n = math.ceil(p_num_reviews/100)
        # low_range = [x*30 for x in list(range(0,max_n))]
        # up_range = [x*30 for x in list(range(1,max_n+1))]

        links3 = ['https://api.bazaarvoice.com/data/reviews.json?Filter=ProductId%3A' +
            p_id + '&Sort=SubmissionTime%3Adesc&Limit=' + 
            '{}&Offset={}&Include=Products%2CComments&'.format(min(int(p_num_reviews - x*100), 100), x*100) +
                  'Stats=Reviews&passkey=rwbw526r2e7spptqd2qzbkp7&apiversion=5.4' for x in list(range(0, max_n))]

        for url in links3:
            # time.sleep(0.5)
            yield Request(url, callback=self.parse_reviews,
                meta={'product': product, 'p_id':p_id, 'p_star':p_star, 'brand_name':brand_name,
                'p_categories':p_categories, 'p_num_reviews':p_num_reviews, 'p_price':p_price,
                'p_hero_image':p_hero_image, 'p_product_url': p_product_url})

    def parse_reviews(self, response):
        # time.sleep(0.5)
        print('parse_reviews')

        product = response.meta['product']
        p_id = response.meta['p_id']
        p_star = response.meta['p_star']
        brand_name = response.meta['brand_name']
        p_price = response.meta['p_price']
        p_categories = response.meta['p_categories']
        p_num_reviews = response.meta['p_num_reviews']
        p_hero_image = response.meta['p_hero_image']
        p_product_url = response.meta['p_product_url']

        data = json.loads(response.text)
        #check keys
        #data.keys()
        reviews = data['Results'] #this is a list
        #each element inside reviews is a dictionary
        #tmp[0].keys() will give the keys of the dictionaries inside reviews

        #create code here which arranges the data from the json dictionary into a dataframe

        n_count = 0
        global n_count_tot, product_count_tot
        count_by_skintype = {}
        rating_by_skintype = {}
        
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

            #need to create an error handler for empty data for reviews

            # print ('BRAND: {} PRODUCT: {}'.format(brand_name, product))
            # print ('ID: {} STARS: {}'.format(reviewer, r_star))
            # print ('='*50)
            count_by_skintype[r_skintype] = count_by_skintype.get(r_skintype, 0) + 1
            rating_by_skintype[r_skintype] = rating_by_skintype.get(r_skintype, 0) + r_star
            
            item = SephoraItem()
            item['product'] = product
            item['p_id'] = p_id
            item['p_star'] = p_star
            item['brand_name'] = brand_name
            item['p_price'] = p_price
            item['p_categories'] = p_categories
            item['p_num_reviews'] = p_num_reviews 
            item['p_product_url'] = p_product_url
            item['p_hero_image'] = p_hero_image

        #all of these needs to be taken from the reviews list/dictionary

            item['reviewer'] = reviewer
            item['r_star'] = r_star
            item['r_eyecolor'] = r_eyecolor
            item['r_haircolor'] = r_haircolor
            item['r_skintone'] = r_skintone
            item['r_skintype'] = r_skintype
            item['r_skinconcerns'] = r_skinconcerns
            item['r_review'] = r_review
            item['r_last_modified_time'] = r_last_modified_time
            item['r_negative_count'] = r_negative_count
            item['r_positive_count'] = r_positive_count
            item['r_userlocation'] = r_userlocation
            item['r_title'] = r_title

            #time.sleep(0.025)
            n_count += 1
            n_count_tot += 1

            yield item

        # time.sleep(20)            
        print ('='*50)
        print ('BRAND: {} PRODUCT: {}'.format(brand_name, product))
        print (count_by_skintype)
        print (rating_by_skintype)
        # print ('TOTAL NUMBER OF REVIEWS: {}'.format(int(p_num_reviews)))
        # print ('TOTAL NUMBER PULLED FOR PRODUCT: {}'.format(len(reviews)))
        # print ('ACTUAL NUMBER PULLED {}'.format(n_count))
        # print ('TOTAL NUMBER PULLED {}'.format(n_count_tot))
        # print ('TOTAL NUMBER PRODUCTS {}'.format(product_count_tot))
        print ('='*50)
        time.sleep(10)

