from scrapy import Spider, Request
from items import IngredientItem, ProductContent
import re
import pandas as pd
import json
import math
import time

# scrapy runspider -s USER_AGENT='Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)' cosdna_spider.py

ARCHIVED_URLS = [
        "http://www.cosdna.com/eng/cosmetic_ec3a411293.html",
        "http://www.cosdna.com/eng/cosmetic_dde3332362.html",
        "http://www.cosdna.com/eng/cosmetic_a529354667.html",
        "http://www.cosdna.com/eng/cosmetic_7ddd377593.html",
        "http://www.cosdna.com/eng/cosmetic_fa56376868.html",
        "http://www.cosdna.com/eng/cosmetic_e5b2360798.html",
        "http://www.cosdna.com/eng/cosmetic_1403380975.html",
        "http://www.cosdna.com/eng/cosmetic_5e74427261.html",
        "http://www.cosdna.com/eng/cosmetic_f8de448825.html",
        "http://www.cosdna.com/eng/cosmetic_7a94387725.html",
        "http://www.cosdna.com/eng/cosmetic_47e5283513.html",
        "http://www.cosdna.com/eng/cosmetic_c25a402077.html",
        "http://www.cosdna.com/eng/cosmetic_312d431514.html",
        "http://www.cosdna.com/eng/cosmetic_a40f276455.html",
        "http://www.cosdna.com/eng/cosmetic_ffd8374394.html",
        "http://www.cosdna.com/eng/cosmetic_8e28155044.html"
    ]

TERA_IDS = {
    "http://www.cosdna.com/eng/cosmetic_b4ed424492.html": 932,
    "http://www.cosdna.com/eng/cosmetic_f431444029.html": 928,
    "http://www.cosdna.com/eng/cosmetic_207f454199.html": 933,
    "http://www.cosdna.com/eng/cosmetic_0f9a448843.html": 931,
    "http://www.cosdna.com/eng/cosmetic_8b3e418940.html": 934,
    "http://www.cosdna.com/eng/cosmetic_5069432144.html": 919,
    "http://www.cosdna.com/eng/cosmetic_e516423644.html": 920,
    "http://www.cosdna.com/eng/cosmetic_188f386642.html": 924,
    "http://www.cosdna.com/eng/cosmetic_7d1a443704.html": 1880,
    "http://www.cosdna.com/eng/cosmetic_fc3e432348.html": 1901,
    "http://www.cosdna.com/eng/cosmetic_9e81443686.html": 4946,
    "http://www.cosdna.com/eng/cosmetic_557d435025.html": 886,
    "http://www.cosdna.com/eng/cosmetic_3b7f447556.html": 4836,
    "http://www.cosdna.com/eng/cosmetic_6ee7452566.html": 645,
    "http://www.cosdna.com/eng/cosmetic_7e88457154.html": 844
}


class CosdnaSpider(Spider):

    name = "cosdna_spider"
    start_urls = [
        "http://www.cosdna.com/eng/cosmetic_b4ed424492.html",
        "http://www.cosdna.com/eng/cosmetic_f431444029.html",
        "http://www.cosdna.com/eng/cosmetic_207f454199.html",
        "http://www.cosdna.com/eng/cosmetic_0f9a448843.html",
        "http://www.cosdna.com/eng/cosmetic_8b3e418940.html",
        "http://www.cosdna.com/eng/cosmetic_5069432144.html",
        "http://www.cosdna.com/eng/cosmetic_e516423644.html",
        "http://www.cosdna.com/eng/cosmetic_188f386642.html",
        "http://www.cosdna.com/eng/cosmetic_7d1a443704.html",
        "http://www.cosdna.com/eng/cosmetic_fc3e432348.html",
        "http://www.cosdna.com/eng/cosmetic_9e81443686.html",
        "http://www.cosdna.com/eng/cosmetic_557d435025.html",
        "http://www.cosdna.com/eng/cosmetic_3b7f447556.html",
        "http://www.cosdna.com/eng/cosmetic_6ee7452566.html",
        "http://www.cosdna.com/eng/cosmetic_7e88457154.html"
    ]

    def parse(self, response):
        product_name = response.xpath('//span[has-class("ProdTitleName")]/text()').extract_first()
        product = ProductContent()
        product['product_name'] = product_name
        product['ingredients'] = []
        ingredients = []
        trs = response.xpath('//tr[@valign="top"]')
        for tr in trs:
            item = IngredientItem()
            item_dict = {}

            item['ingredient_name'] = tr.xpath('td[@class="iStuffETitle"]/a/text()').extract_first()
            item_dict['ingredient_name'] = item['ingredient_name']
            item['function'] = [x[1:] for x in tr.xpath('td/span[@class="iStuffChar"]/text()').extract()]
            item_dict['function'] = item['function']

            acne_irr = tr.xpath('td/span[@style="color: red"]/text()').extract()
            if len(acne_irr) > 1:
                item['irr_rating'] = acne_irr[1]
            else:
                item['irr_rating'] = '0'
            item_dict['irr_rating'] = item['irr_rating']

            if len(acne_irr) > 0:
                item['acne_rating'] = acne_irr[0]
            else:
                item['acne_rating'] = '0'
            item_dict['acne_rating'] = item['acne_rating']

            lower_bound = tr.xpath('td/span[@class="SafetyL"]/text()').extract_first()
            upper_bound = tr.xpath('td/span[@class="SafetyM"]/text()').extract_first()
            if lower_bound:
                item['safe_rating'] = lower_bound
                if upper_bound:
                    item['safe_rating'] += "-" + upper_bound
            else:
                item['safe_rating'] = '0'
            item_dict['safe_rating'] = item['safe_rating']

            product['ingredients'].append(item)
            ingredients.append(item_dict)

        moisturizer = 0
        emollient = 0
        antioxidant = 0
        anti_inflammatory = 0
        anti_allergic = 0
        astringent = 0
        # cell_regeneration = 0
        acne = 0
        irritant = 0
        hazard = 0

        increment = 0.25
        start = 10
        non_sunscreen = filter(lambda x: 'Sunscreen' not in x['function'], product['ingredients'])
        for num, ingredient in enumerate(non_sunscreen):
            weight = start - num * increment
            if weight < 0:
                weight = 0
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
            if 'Astringent' in ingredient['function']:
                astringent += 1 * weight

            acne_rating = [int(x) for x in ingredient['acne_rating'].split('-')]
            irr_rating = [int(x) for x in ingredient['irr_rating'].split('-')]
            safe_rating = [int(x) for x in ingredient['safe_rating'].split('-')]
            acne += sum(acne_rating)/len(acne_rating) * weight
            irritant += sum(irr_rating)/len(irr_rating) * weight
            hazard += sum(safe_rating)/len(safe_rating) * weight

        print("*"*100)
        print('ingredients', ingredients)
        print('moisturizer: ', moisturizer)
        print('emollient: ', emollient)
        print('astringent: ', astringent)
        print('antioxidant: ', antioxidant)
        print('anti_inflammatory: ', anti_inflammatory)
        print('anti_allergic: ', anti_allergic)
        print('acne: ', acne)
        print('irritant: ', irritant)
        print('hazard: ', hazard)

        product_id = TERA_IDS[response.request.url]
        res = {
            "product_id": product_id,
            "product_name": product['product_name'],
            "ingredients":  ingredients,
            "moisturizer": moisturizer,
            "emollient": emollient,
            "astringent": astringent,
            "antioxidant": antioxidant,
            "anti_inflammatory": anti_inflammatory,
            "anti_allergic": anti_allergic,
            "acne": acne,
            "irritant": irritant,
            "hazard": hazard
        }

        # write res to the ingredients.json file
        with open("./data/ingredients.json", "a") as output:
            line = json.dumps(res) + ",\n"
            output.write(line)
