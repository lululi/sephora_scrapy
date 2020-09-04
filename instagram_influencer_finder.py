import re
from selenium import webdriver as WebDriver
from selenium.webdriver.common.keys import Keys
from time import sleep, strftime
from random import randint
import random
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def scrape_influencer_by_hashtag():
    visited_users = set()
    with WebDriver.Firefox() as webdriver:
        wait = WebDriverWait(webdriver, 10)
        webdriver.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
        sleep(1)

        username = webdriver.find_element_by_name('username')
        username.send_keys('hello@glowism.com')
        password = webdriver.find_element_by_name('password')
        password.send_keys('glowglow2020')

        button_login = webdriver.find_element_by_xpath("//button[./div/text()='Log In']")
        button_login.click()
        button_notnow = WebDriverWait(webdriver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//button[./text()='Not Now']")))
        button_notnow.click()
        sleep(2)

        hashtag_list = ['skinpositivity']
        with open('influencer_list.txt', 'w') as f:
            for hashtag in hashtag_list:
                webdriver.get('https://www.instagram.com/explore/tags/' + hashtag + '/')
                sleep(1)
                first_thumbnail = webdriver.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div')

                first_thumbnail.click()
                sleep(randint(1, 2))
                influencer = 0
                counter = 0

                while counter < 2000 and influencer < 1000:
                    try:
                        username = WebDriverWait(webdriver, 4   ).until(
                            EC.visibility_of_element_located((By.XPATH, '//a[@class="sqdOP yWX7d     _8A5w5   ZIAjV "]'))).text
                        print(influencer)
                        print(username)

                        # if username in visited_users:
                        #     influencer += 1
                        #     continue

                        if username not in visited_users:
                            visited_users.add(username)
                            line = username + '\n'
                            f.write(line)
                            influencer += 1

                        counter += 1

                        button_next = webdriver.find_element_by_xpath("//a[./text()='Next']")
                        button_next.click()
                        wait_time = random.uniform(2, 6)
                        sleep(wait_time)
                    except Exception as e:
                        print(e)
                        continue


def scrape_detail_info():
    influencer_list = [line.rstrip('\n') for line in open('influencer_list.txt', 'r')]
    with WebDriver.Firefox() as webdriver:
        # wait = WebDriverWait(webdriver, 10)
        # webdriver.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
        # sleep(1)
        #
        # username = webdriver.find_element_by_name('username')
        # username.send_keys('chenyaoli19@gmail.com')
        # password = webdriver.find_element_by_name('password')
        # password.send_keys('2iR^dA0i$5')
        #
        # button_login = webdriver.find_element_by_xpath("//button[./div/text()='Log In']")
        # button_login.click()
        # button_notnow = WebDriverWait(webdriver, 10).until(
        #     EC.visibility_of_element_located((By.XPATH, "//button[./text()='Not Now']")))
        # button_notnow.click()
        # sleep(2)
        idx = 0

        with open('influencer_info.txt', 'a') as f:
            for username in influencer_list:
                if idx < 986:
                    idx += 1
                    print("********")
                    print(idx)
                    print('skip')
                    continue

                try:
                    base_url = 'https://www.instagram.com/'
                    link = base_url + username + '/'
                    webdriver.get(link)
                    sleep(1)

                    followers = webdriver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a').text
                    followers = followers.replace(",", "")
                    name = webdriver.find_element_by_xpath('//*[@class="-vDIg"]/h1').text
                    if name:
                        name = name.replace(",", "|")
                    bio_website = None
                    try:
                        bio_website = webdriver.find_element_by_xpath('//*[@class="-vDIg"]/a').text
                    except:
                        pass
                    if bio_website.startswith('Followed by'):
                        bio_website = None
                    bio = webdriver.find_element_by_xpath('//*[@class="-vDIg"]/span').text
                    match = re.search(r'[\w\.-]+@[\w\.-]+', bio)
                    email = None
                    if match:
                        email = match.group(0)

                    line = ''
                    line += '@' + username + ','
                    line += followers + ','
                    line += name + ',' if name else ','
                    line += email + ',' if email else ','
                    line += bio_website + '\n' if bio_website else '\n'
                    f.write(line)
                    print("*******")
                    print(idx)
                    print(username)
                    print(followers)
                    print(name)
                    print(email)
                    print(bio_website)

                    wait_time = random.uniform(1, 3)
                    sleep(wait_time)
                    idx += 1
                except:
                    continue


def main():
    # scrape_influencer_by_hashtag()
    scrape_detail_info()


if __name__ == '__main__':
    main()
