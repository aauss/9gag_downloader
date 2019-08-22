import requests
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

driver = webdriver.Chrome(executable_path=r"/Users/aussabbood/github/9gag_downloader/chromedriver")

def site_login():
    driver.get("https://9gag.com/")
    time.sleep(5)
    driver.find_element(By.XPATH, '//button[text()="Got it, thanks!"]')
    driver.find_element_by_id("jsid-login-button").click()
    driver.find_element_by_id("username").send_keys("")
    driver.find_element_by_id("passwort").send_keys("")
    driver.find_element_by_id("submit").click()
site_login()
username = ""
likes = requests.get(f"https://9gag.com/u/{username}/likes")
soup = BeautifulSoup(likes.content)
print(soup)
