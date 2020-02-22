import os
import time
import urllib.request

import click
from bs4 import BeautifulSoup
from selenium import webdriver


class Scraper:
    def __init__(self, email: str, password: str, username: str):
        self.email = email
        self.password = password
        self.username = username
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"))

    def log_into_upvotes_page(self):
        self.driver.get("https://9gag.com")
        time.sleep(1)
        self.driver.find_element_by_xpath(
            "/html/body/div[7]/div[1]/div[2]/div/span"
        ).click()  # dismiss cookie warning
        time.sleep(1)
        self.driver.find_element_by_xpath(
            "/html/body/header/div/div/div[2]/a[1]"
        ).click()  # login button
        time.sleep(1)
        self.driver.find_element_by_xpath(
            "/html/body/div[2]/div[3]/section/section/div/form/div[1]/input"
        ).send_keys(self.email)
        self.driver.find_element_by_xpath(
            "/html/body/div[2]/div[3]/section/section/div/form/div[2]/input"
        ).send_keys(self.password)
        self.driver.find_element_by_xpath(
            "/html/body/div[2]/div[3]/section/section/div/form/div[3]/input"
        ).click()
        time.sleep(1)
        self.driver.get(f"https://9gag.com/u/{self.username}/likes")

    def scrape_upvotes(self):
        body = self.driver.find_element_by_css_selector("body")
        # while True:
        soup = BeautifulSoup(self.driver.page_source, features="html.parser")
        section_of_posts = soup.find("section", {"id": "list-view-2"})
        image_urls = self.find_img_urls(section_of_posts)
        video_urls = self.find_video_urls(section_of_posts)
        urls_to_scrape = image_urls + video_urls
        for _ in range(len(urls_to_scrape)):
            body.send_keys("j")
            time.sleep(1)
            print("scroll")
        for url in urls_to_scrape:
            self.download_from_url(url)

    @staticmethod
    def find_img_urls(section_of_posts):
        images_in_section = section_of_posts.find_all_next(
            "img", alt=True
        )  # only images of interest have an alt tag
        image_urls = [image["src"] for image in images_in_section]
        full_size_image_urls = [
            url.replace("460s.jpg", "700b.jpg") for url in image_urls
        ]
        return full_size_image_urls

    @staticmethod
    def find_video_urls(section_of_posts):
        videos_in_section = section_of_posts.find_all_next("video")
        video_urls = [video.find("source")["src"] for video in videos_in_section]
        return video_urls

    @staticmethod
    def download_from_url(url: str):
        table = str.maketrans(r"\/", "||")
        filename = url.translate(table)
        if "jpg" in url:
            filename += ".jpg"
        elif "mp4" in url:
            filename += "mp4"
        urllib.request.urlretrieve(url, filename)


@click.command()
@click.option("--email", "-e", help="your 9gag account email", type=str, prompt=True)
@click.option(
    "--password",
    "-p",
    help="your 9gag account password",
    type=str,
    prompt=True,
    hide_input=True,
)
@click.option("--username", "-p", help="your 9gag username", type=str, prompt=True)
def main(
        email, password, username,
):
    scraper = Scraper(email, password, username)
    time.sleep(1)
    scraper.log_into_upvotes_page()
    time.sleep(1)
    scraper.scrape_upvotes()


if __name__ == "__main__":
    main()
