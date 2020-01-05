from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep, strftime
from random import randint
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

prev_user_list = [line.rstrip('\n') for line in open('users_advertised_list.txt', 'r')]

comment_dict = {
    1: "Nice!",
    2: "Love your feed!",
    3: "Great content!!",
    4: "🙌🙌🙌",
    5: "❤️ xoxo",
    7: "Keep them coming! 🤗",
    8: "😍😍😍",
    9: "Nailed it!👏",
    10: "Love it!"
}

ad = "Great info!👏 If you care about what you put on your face, we recently launched a search engine for skincare at glowism.com. You could look up skincare products' ingredients information and reviews. You could also create a skin profile to have the information personalized for you. Check it out and let us know what you think 🥰'"

with webdriver.Firefox() as webdriver:
    wait = WebDriverWait(webdriver, 10)
    webdriver.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
    sleep(1)
    
    username = webdriver.find_element_by_name('username')
    username.send_keys('glowism_')
    password = webdriver.find_element_by_name('password')
    password.send_keys('t3rat3ra2019')

    button_login = webdriver.find_element_by_xpath("//button[./div/text()='Log In']")
    button_login.click()
    button_notnow = WebDriverWait(webdriver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//button[./text()='Not Now']")))
    button_notnow.click()
    sleep(2)
    
    hashtag_list = ['skinscience']
    for hashtag in hashtag_list:
        webdriver.get('https://www.instagram.com/explore/tags/'+ hashtag + '/')
        sleep(1)
        first_thumbnail = webdriver.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div')
    
        first_thumbnail.click()
        sleep(randint(1,2))
        likes = 0

        while likes < 100:
            try:        
                username = WebDriverWait(webdriver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, '//a[@class="FPmhX notranslate  nJAzx"]'))).text
                button_like = webdriver.find_element_by_xpath('//span[starts-with(@class,"glyphsSpriteHeart__")]')
                if button_like.get_attribute("aria-label") == "Like":
                    button_like.click()
                    likes += 1
                    comment_box = webdriver.find_element_by_xpath('//textarea[@class="Ypffh"]')
                    comment_box.click()
                    comment = ''
                    comm_choice = randint(1,10)
                    comment = comment_dict[comm_choice]

                    # if username in prev_user_list:
                    #     comm_choice = randint(1,10)
                    #     comment = comment_dict[comm_choice]
                    # else:
                    #     comment = ad
                    #     prev_user_list.append(username)
                    print(comment)
                    comment_box = webdriver.find_element_by_xpath('//textarea[starts-with(@class, "Ypffh")]')
                    comment_box.send_keys(comment)
                    comment_box.send_keys(Keys.ENTER)
                    sleep(randint(20, 30))
                button_next = webdriver.find_element_by_xpath("//a[./text()='Next']")
                button_next.click()
                sleep(randint(1,2))
            except Exception as e:
                print(e)
                continue        

    content = ''
    for item in prev_user_list:
        content += item + '\n'
    with open('users_advertised_list.txt', 'w') as f:
        f.write(content)
