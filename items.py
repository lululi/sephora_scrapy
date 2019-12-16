# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
import json
import scrapy
from scrapy.loader.processors import TakeFirst, Identity


class ReviewItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    brand_name = scrapy.Field()
    product = scrapy.Field()
    p_id = scrapy.Field()
    p_star = scrapy.Field()
    p_category = scrapy.Field()
    # if there are multiple prices, this will be a list field sorting from the least
    # expensive to most
    p_prices = scrapy.Field()
    # if there are multiple sizes, this will be a list field sorting from the smallest
    # to the largest
    p_sizes = scrapy.Field()
    p_num_reviews = scrapy.Field()
    p_tags = scrapy.Field()
    reviewer = scrapy.Field()
    r_star = scrapy.Field()
    r_eyecolor = scrapy.Field()
    r_haircolor = scrapy.Field()
    r_skintone = scrapy.Field()
    r_skintype = scrapy.Field()
    r_skinconcerns = scrapy.Field()
    r_review = scrapy.Field()
    r_last_modified_time = scrapy.Field()
    r_negative_count = scrapy.Field()
    r_positive_count = scrapy.Field()
    r_userlocation = scrapy.Field()
    r_title = scrapy.Field()
    r_age = scrapy.Field()
    r_gender = scrapy.Field()
    p_product_url = scrapy.Field()
    p_hero_image = scrapy.Field()
    p_large_image = scrapy.Field()


class ProductContent(scrapy.Item):
    product_name = scrapy.Field()
    ingredients = scrapy.Field()


class IngredientItem(scrapy.Item):
    ingredient_name = scrapy.Field()
    function = scrapy.Field()
    acne_rating = scrapy.Field()
    irr_rating = scrapy.Field()
    safe_rating = scrapy.Field()


class EwgScraperIngredient(scrapy.Item):
    # define the fields for ingredients
    # name = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    ingredient_id = scrapy.Field(output_processor=TakeFirst())
    ingredient_name = scrapy.Field(output_processor=TakeFirst())
    ingredient_score = scrapy.Field(output_processor=TakeFirst())
    data_availability = scrapy.Field(output_processor=TakeFirst())
    overall_hazard_score = scrapy.Field(output_processor=TakeFirst())
    cancer_score = scrapy.Field(output_processor=TakeFirst())
    dev_reprod_tox_score = scrapy.Field(output_processor=TakeFirst())
    allergy_imm_tox_score = scrapy.Field(output_processor=TakeFirst())
    use_restrict_score = scrapy.Field(output_processor=TakeFirst())
    synonym_list = scrapy.Field(output_processor=Identity())
    function_list = scrapy.Field(output_processor=Identity())


class EwgScraperProduct(scrapy.Item):
    # Define the fields for Products
    url = scrapy.Field(output_processor=TakeFirst())
    product_id = scrapy.Field(output_processor=TakeFirst())
    product_name = scrapy.Field(output_processor=TakeFirst())
    product_score = scrapy.Field(output_processor=TakeFirst())
    product_type = scrapy.Field(output_processor=TakeFirst())
    data_availability = scrapy.Field(output_processor=TakeFirst())
    overall_hazard_score = scrapy.Field(output_processor=TakeFirst())
    cancer_score = scrapy.Field(output_processor=TakeFirst())
    dev_reprod_tox_score = scrapy.Field(output_processor=TakeFirst())
    allergy_imm_tox_score = scrapy.Field(output_processor=TakeFirst())
    use_restrict_score = scrapy.Field(output_processor=TakeFirst())
    ingredient_list = scrapy.Field(output_processor=Identity())
