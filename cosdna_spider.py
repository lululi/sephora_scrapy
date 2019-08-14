from scrapy import Spider, Request
from items import IngredientItem, ProductContent
import re
import pandas as pd
import json
import math
import time

# scrapy runspider -s USER_AGENT='Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)' cosdna_spider.py
class CosdnaSpider(Spider):

    name = "cosdna_spider"
    start_urls = ["http://www.cosdna.com/eng/cosmetic_ec3a411293.html"]
    def parse(self, response):
        product_name = response.xpath('//span[has-class("ProdTitleName")]/text()').extract_first()
        product = ProductContent()
        product['product_name'] = product_name
        product['ingredients'] = []
        trs = response.xpath('//tr[@valign="top"]')
        for tr in trs:
            item = IngredientItem()
            item['ingredient_name'] = tr.xpath('td[@class="iStuffETitle"]/a/text()').extract_first()
            item['function'] = [x[1:] for x in tr.xpath('td/span[@class="iStuffChar"]/text()').extract()]
            acne_irr = tr.xpath('td/span[@style="color: red"]/text()').extract()
            if len(acne_irr) > 1:
                item['irr_rating'] = acne_irr[1]
            else:
                item['irr_rating'] = '0'
            if len(acne_irr) > 0:
                item['acne_rating'] = acne_irr[0]
            else:
                item['acne_rating'] = '0'
            lower_bound = tr.xpath('td/span[@class="SafetyL"]/text()').extract_first()
            upper_bound = tr.xpath('td/span[@class="SafetyM"]/text()').extract_first()
            if lower_bound:
                item['safe_rating'] = lower_bound
                if upper_bound:
                    item['safe_rating'] += "-" + upper_bound
            else:
                item['safe_rating'] = '0'
            product['ingredients'].append(item)

        moisturizer = 0
        emollient = 0
        antioxidant = 0
        anti_inflammatory = 0
        anti_allergic = 0
        astrigent = 0
        # cell_regeneration = 0
        acne = 0
        irritant = 0
        hazard = 0

        increment = 0.25
        start = 10
        non_sunscreen = filter(lambda x: 'Sunscreen' not in x['function'], product['ingredients'])
        for num, ingredient in enumerate(non_sunscreen):
            weight = start - num * increment
            if 'Moisturizer' in ingredient['function']:
                moisturizer += 1 * weight
            if 'Emollient' in ingredient['function']:
                emollient += 1 * weight
            if 'Antioxidant' in ingredient['function']:
                antioxidant += 1 * weight
            if 'Anti-inflammatory' in ingredient['function']:
                anti_inflammatory += 1 * weight
            if 'Anti-allergic' in ingredient['function']:
                anti_allergic += 1 * weight
            if 'Astrigent' in ingredient['function']:
                astrigent += 1 * weight

            acne_rating = [int(x) for x in ingredient['acne_rating'].split('-')]
            irr_rating = [int(x) for x in ingredient['irr_rating'].split('-')]
            safe_rating = [int(x) for x in ingredient['safe_rating'].split('-')]
            acne += sum(acne_rating)/len(acne_rating) * weight
            irritant += sum(irr_rating)/len(irr_rating) * weight
            hazard += sum(safe_rating)/len(safe_rating) * weight

        print('moisturizer: ', moisturizer)
        print('emollient: ', emollient)
        print('astrigent: ', astrigent)
        print('antioxidant: ', antioxidant)
        print('anti_inflammatory: ', anti_inflammatory)
        print('anti_allergic: ', anti_allergic)

        print('acne: ', acne)
        print('irritant: ', irritant)
        print('hazard: ', hazard)
        yield product
        
