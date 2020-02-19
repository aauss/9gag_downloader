import click
import requests
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

driver = webdriver.Chrome(executable_path=r"/Users/aussabbood/github/9gag_downloader/chromedriver")

@click.command()
@click.option("--email", "-e", help="your 9gag account email", type=str, prompt=True)
@click.option("--password", "-p", help="your 9gag account password", type=str, prompt=True, hide_input=True)
@click.option("--username", "-p", help="your 9gag username", type=str, prompt=True)
def site_login(email, password, username):
    driver.get("https://9gag.com/")
    driver.find_element_by_xpath("/html/body/div[7]/div[1]/div[2]/div/span").click()  #dismiss cookie warning
    time.sleep(0.5)
    driver.find_element_by_xpath("/html/body/header/div/div/div[2]/a[1]").click()  #login button
    time.sleep(0.5)
    driver.find_element_by_xpath("/html/body/div[2]/div[3]/section/section/div/form/div[1]/input").send_keys(email)
    driver.find_element_by_xpath("/html/body/div[2]/div[3]/section/section/div/form/div[2]/input").send_keys(password)
    driver.find_element_by_xpath("/html/body/div[2]/div[3]/section/section/div/form/div[3]/input").click()
    time.sleep(0.4)
    driver.get(f"https://9gag.com/u/{username}/likes")


if __name__=="__main__":
    site_login()
