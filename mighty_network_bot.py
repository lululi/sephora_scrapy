from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep, strftime
from random import randint
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

with webdriver.Firefox() as webdriver:
    wait = WebDriverWait(webdriver, 10)

    webdriver.get('https://www.skincare-junkie.com/new-members')
    sleep(5)

    for i in range(1, 2):
        webdriver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(randint(1, 5))

    elements = webdriver.find_elements(By.CLASS_NAME, 'member-list-item')
    user_ids = [x.get_attribute('data-member-item') for x in elements]

    sleep(randint(10, 30))
    webdriver.get('https://www.skincare-junkie.com/sign_in')
    sleep(5)

    email_field = webdriver.find_element(By.CLASS_NAME, 'email-input')
    email_field.send_keys('experisy@gmail.com')
    next_button = webdriver.find_element(By.CLASS_NAME, 'submit-button')
    next_button.click()
    password_field = webdriver.find_element(By.CLASS_NAME, 'password-input')
    password_field.send_keys('5?58BHDq@Z4FkKW')
    sleep(randint(3, 5))

    next_button = webdriver.find_element(By.CLASS_NAME, 'submit-button')
    next_button.click()
    sleep(randint(10, 20))

    count = 0
    for user_id in user_ids:
        webdriver.get('https://www.skincare-junkie.com/chats/new?user_id=' + user_id)
        sleep(randint(5, 10))
        try:
            empty_chat_header = webdriver.find_element(By.CLASS_NAME, 'empty-chat-list-pair')
            name = empty_chat_header.find_element(By.CLASS_NAME, 'text-color-title-link').text
            print(name)
            chat_input = webdriver.find_element(By.ID, 'popout-chat-input-text')
            chat_input.send_keys(
                "Hi " + name + ', welcome to the community! '
                "Sorry to message out of blue, just thought this might be helpful." + "\r\r"
                "After my friend's endless research looking for creams to soothe her eczema, we launched a skincare app "
                "a couple of months ago to provide trustworthy and personalized skincare guidance by curated skincare "
                "professionals. We partnered with Stanford dermatologists and found a selected few licensed "
                "estheticians among 100+ candidates. Now we're trying to \"get the word out\" to people who"
                "need skincare help. Would love to know what you think of the idea? You could check it out "
                "at https://glowism.com" + "\r\r"
                "No worries if you're too busy to reply. I understand life could be pretty hectic "
                "under the current situation. :)"
            )
            chat_input.send_keys(Keys.RETURN)
            count += 1
        except Exception as e:
            print("UserId:", user_id, " Error:", e)
        sleep(randint(5, 10))
    print('Total users sent:', count)
