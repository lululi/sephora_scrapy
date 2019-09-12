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
        "http://www.cosdna.com/eng/cosmetic_8e28155044.html",
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

TERA_IDS = {
    "http://cosdna.com/eng/cosmetic_7aac411151.html": 1366,
    "http://cosdna.com/eng/cosmetic_5168225903.html": 1370,
    "http://cosdna.com/eng/cosmetic_db0a386134.html": 1380,
    "http://cosdna.com/eng/cosmetic_3435459218.html": 1384,
    "http://cosdna.com/eng/cosmetic_2c0c448692.html": 1379,
    "http://cosdna.com/eng/cosmetic_8ca8284091.html": 5116,
    "http://cosdna.com/eng/cosmetic_ce9c346152.html": 1811,
    "http://cosdna.com/eng/cosmetic_91af406815.html": 1148,
    "http://cosdna.com/eng/cosmetic_c572452731.html": 1343,
    "http://cosdna.com/eng/cosmetic_ebfc458754.html": 4997,
    "http://cosdna.com/eng/cosmetic_2f91455738.html": 4995,
    "http://cosdna.com/eng/cosmetic_29b9403705.html": 2965,
    "http://cosdna.com/eng/cosmetic_3cb7457540.html": 5550,
    "http://cosdna.com/eng/cosmetic_ae79425546.html": 5555,
    "http://cosdna.com/eng/cosmetic_404b448826.html": 1377,

    "http://cosdna.com/eng/cosmetic_bdc0419449.html": 1896,
    "http://cosdna.com/eng/cosmetic_8be5414211.html": 5038,
    "http://cosdna.com/eng/cosmetic_1f59438011.html": 1661,
    "http://cosdna.com/eng/cosmetic_f4d9387861.html": 1874,
    "http://cosdna.com/eng/cosmetic_1b89267709.html": 788,
    "http://cosdna.com/eng/cosmetic_1ae2417920.html": 4519,
    "http://cosdna.com/eng/cosmetic_6534312700.html": 1607,
    "http://cosdna.com/eng/cosmetic_50ba401595.html": 1908,
    "http://cosdna.com/eng/cosmetic_ce08459598.html": 1904,
    "http://cosdna.com/eng/cosmetic_f616436920.html": 1905,
    "http://cosdna.com/eng/cosmetic_33a0461540.html": 1902,
    "http://cosdna.com/eng/cosmetic_28e9448720.html": 1891,
    "http://cosdna.com/eng/cosmetic_f890382141.html": 1895,
    "http://cosdna.com/eng/cosmetic_ce8b397503.html": 428,
    "http://cosdna.com/eng/cosmetic_339f370378.html": 5553,
    "http://cosdna.com/eng/cosmetic_2eed337809.html": 5549,

    "http://cosdna.com/eng/cosmetic_aea0435370.html": 2115,
    "http://cosdna.com/eng/cosmetic_14f8423262.html": 2109,
    "http://cosdna.com/eng/cosmetic_c57b423394.html": 2105,
    "http://cosdna.com/eng/cosmetic_e83a454911.html": 2110,
    "http://cosdna.com/eng/cosmetic_6d15455084.html": 2114,
    "http://cosdna.com/eng/cosmetic_abeb441268.html": 2106,
    "http://cosdna.com/eng/cosmetic_35ee420680.html": 3870,
    "http://cosdna.com/eng/cosmetic_1230451924.html": 2100,
    "http://cosdna.com/eng/cosmetic_25e0280269.html": 3868,
    "http://cosdna.com/eng/cosmetic_c8e5316585.html": 4062,
    "http://cosdna.com/eng/cosmetic_61af342249.html": 1994,
    "http://cosdna.com/eng/cosmetic_d4df443855.html": 5552,
    "http://cosdna.com/eng/cosmetic_8711459219.html": 2103,

    "http://cosdna.com/eng/cosmetic_8d43459597.html": 2459,
    "http://cosdna.com/eng/cosmetic_a7bb447961.html": 2458,
    "http://cosdna.com/eng/cosmetic_1895449074.html": 2457,
    "http://cosdna.com/eng/cosmetic_8d84384311.html": 2433,
    "http://cosdna.com/eng/cosmetic_0b7e427504.html": 2442,
    "http://cosdna.com/eng/cosmetic_a8ab443567.html": 2453,
    "http://cosdna.com/eng/cosmetic_d47c448495.html": 2449,
    "http://cosdna.com/eng/cosmetic_1621346187.html": 2427,
    "http://cosdna.com/eng/cosmetic_ded6428396.html": 2451,
    "http://cosdna.com/eng/cosmetic_b643254917.html": 2445,
    "http://cosdna.com/eng/cosmetic_dedf396748.html": 2393,
    "http://cosdna.com/eng/cosmetic_39e7437197.html": 4743,
    "http://cosdna.com/eng/cosmetic_e444258193.html": 5548,

    "http://cosdna.com/eng/cosmetic_932f448836.html": 1372,
    "http://cosdna.com/eng/cosmetic_3d94436553.html": 1371,
    "http://cosdna.com/eng/cosmetic_b394444365.html": 1375,
    "http://cosdna.com/eng/cosmetic_3ba6357921.html": 1859,
    "http://cosdna.com/eng/cosmetic_9c54323834.html": 1348,
    "http://cosdna.com/eng/cosmetic_1a85374731.html": 1351,
    "http://cosdna.com/eng/cosmetic_caf4450606.html": 1865,
    "http://cosdna.com/eng/cosmetic_01e8426879.html": 1300,
    "http://cosdna.com/eng/cosmetic_62b7134721.html": 1287,
    "http://cosdna.com/eng/cosmetic_4061295766.html": 1238,
    "http://cosdna.com/eng/cosmetic_c0d9406020.html": 2941,
    "http://cosdna.com/eng/cosmetic_3d66430633.html": 4731,
    "http://cosdna.com/eng/cosmetic_d58c444058.html": 5551,

    "http://cosdna.com/eng/cosmetic_f890382141.html": 1895,
    "http://cosdna.com/eng/cosmetic_4023323202.html": 1369,
    "http://cosdna.com/eng/cosmetic_3612440240.html": 1376,
    "http://cosdna.com/eng/cosmetic_b016439576.html": 1346,
    "http://cosdna.com/eng/cosmetic_cda8461095.html": 1385,
    "http://cosdna.com/eng/cosmetic_2af4409853.html": 1368,
    "http://cosdna.com/eng/cosmetic_ce84442537.html": 1367,
    "http://cosdna.com/eng/cosmetic_6677309464.html": 1303,
    "http://cosdna.com/eng/cosmetic_0531451741.html": 877,
    "http://cosdna.com/eng/cosmetic_cf2a341190.html": 1822,
    "http://cosdna.com/eng/cosmetic_c943257878.html": 2976,
    "http://cosdna.com/eng/cosmetic_92b4452044.html": 2998,
    "http://cosdna.com/eng/cosmetic_2e1a458338.html": 3693,
    "http://cosdna.com/eng/cosmetic_fa97455763.html": 1361,
    "http://cosdna.com/eng/cosmetic_5a60297928.html": 5554
}


class CosdnaSpider(Spider):

    name = "cosdna_spider"
    start_urls = [
        "http://cosdna.com/eng/cosmetic_7aac411151.html",
        "http://cosdna.com/eng/cosmetic_5168225903.html",
        "http://cosdna.com/eng/cosmetic_db0a386134.html",
        "http://cosdna.com/eng/cosmetic_3435459218.html",
        "http://cosdna.com/eng/cosmetic_2c0c448692.html",
        "http://cosdna.com/eng/cosmetic_8ca8284091.html",
        "http://cosdna.com/eng/cosmetic_ce9c346152.html",
        "http://cosdna.com/eng/cosmetic_91af406815.html",
        "http://cosdna.com/eng/cosmetic_c572452731.html",
        "http://cosdna.com/eng/cosmetic_ebfc458754.html",
        "http://cosdna.com/eng/cosmetic_2f91455738.html",
        "http://cosdna.com/eng/cosmetic_29b9403705.html",
        "http://cosdna.com/eng/cosmetic_3cb7457540.html",
        "http://cosdna.com/eng/cosmetic_ae79425546.html",
        "http://cosdna.com/eng/cosmetic_404b448826.html",
        "http://cosdna.com/eng/cosmetic_bdc0419449.html",
        "http://cosdna.com/eng/cosmetic_8be5414211.html",
        "http://cosdna.com/eng/cosmetic_1f59438011.html",
        "http://cosdna.com/eng/cosmetic_f4d9387861.html",
        "http://cosdna.com/eng/cosmetic_1b89267709.html",
        "http://cosdna.com/eng/cosmetic_1ae2417920.html",
        "http://cosdna.com/eng/cosmetic_6534312700.html",
        "http://cosdna.com/eng/cosmetic_50ba401595.html",
        "http://cosdna.com/eng/cosmetic_ce08459598.html",
        "http://cosdna.com/eng/cosmetic_f616436920.html",
        "http://cosdna.com/eng/cosmetic_33a0461540.html",
        "http://cosdna.com/eng/cosmetic_28e9448720.html",
        "http://cosdna.com/eng/cosmetic_f890382141.html",
        "http://cosdna.com/eng/cosmetic_ce8b397503.html",
        "http://cosdna.com/eng/cosmetic_339f370378.html",
        "http://cosdna.com/eng/cosmetic_2eed337809.html",
        "http://cosdna.com/eng/cosmetic_aea0435370.html",
        "http://cosdna.com/eng/cosmetic_14f8423262.html",
        "http://cosdna.com/eng/cosmetic_c57b423394.html",
        "http://cosdna.com/eng/cosmetic_e83a454911.html",
        "http://cosdna.com/eng/cosmetic_6d15455084.html",
        "http://cosdna.com/eng/cosmetic_abeb441268.html",
        "http://cosdna.com/eng/cosmetic_35ee420680.html",
        "http://cosdna.com/eng/cosmetic_1230451924.html",
        "http://cosdna.com/eng/cosmetic_25e0280269.html",
        "http://cosdna.com/eng/cosmetic_c8e5316585.html",
        "http://cosdna.com/eng/cosmetic_61af342249.html",
        "http://cosdna.com/eng/cosmetic_d4df443855.html",
        "http://cosdna.com/eng/cosmetic_8711459219.html",
        "http://cosdna.com/eng/cosmetic_8d43459597.html",
        "http://cosdna.com/eng/cosmetic_a7bb447961.html",
        "http://cosdna.com/eng/cosmetic_1895449074.html",
        "http://cosdna.com/eng/cosmetic_8d84384311.html",
        "http://cosdna.com/eng/cosmetic_0b7e427504.html",
        "http://cosdna.com/eng/cosmetic_a8ab443567.html",
        "http://cosdna.com/eng/cosmetic_d47c448495.html",
        "http://cosdna.com/eng/cosmetic_1621346187.html",
        "http://cosdna.com/eng/cosmetic_ded6428396.html",
        "http://cosdna.com/eng/cosmetic_b643254917.html",
        "http://cosdna.com/eng/cosmetic_dedf396748.html",
        "http://cosdna.com/eng/cosmetic_39e7437197.html",
        "http://cosdna.com/eng/cosmetic_e444258193.html",
        "http://cosdna.com/eng/cosmetic_932f448836.html",
        "http://cosdna.com/eng/cosmetic_3d94436553.html",
        "http://cosdna.com/eng/cosmetic_b394444365.html",
        "http://cosdna.com/eng/cosmetic_3ba6357921.html",
        "http://cosdna.com/eng/cosmetic_9c54323834.html",
        "http://cosdna.com/eng/cosmetic_1a85374731.html",
        "http://cosdna.com/eng/cosmetic_caf4450606.html",
        "http://cosdna.com/eng/cosmetic_01e8426879.html",
        "http://cosdna.com/eng/cosmetic_62b7134721.html",
        "http://cosdna.com/eng/cosmetic_4061295766.html",
        "http://cosdna.com/eng/cosmetic_c0d9406020.html",
        "http://cosdna.com/eng/cosmetic_3d66430633.html",
        "http://cosdna.com/eng/cosmetic_d58c444058.html",
        "http://cosdna.com/eng/cosmetic_f890382141.html",
        "http://cosdna.com/eng/cosmetic_4023323202.html",
        "http://cosdna.com/eng/cosmetic_3612440240.html",
        "http://cosdna.com/eng/cosmetic_b016439576.html",
        "http://cosdna.com/eng/cosmetic_cda8461095.html",
        "http://cosdna.com/eng/cosmetic_2af4409853.html",
        "http://cosdna.com/eng/cosmetic_ce84442537.html",
        "http://cosdna.com/eng/cosmetic_6677309464.html",
        "http://cosdna.com/eng/cosmetic_0531451741.html",
        "http://cosdna.com/eng/cosmetic_cf2a341190.html",
        "http://cosdna.com/eng/cosmetic_c943257878.html",
        "http://cosdna.com/eng/cosmetic_92b4452044.html",
        "http://cosdna.com/eng/cosmetic_2e1a458338.html",
        "http://cosdna.com/eng/cosmetic_fa97455763.html",
        "http://cosdna.com/eng/cosmetic_5a60297928.html"
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
