import time
from pathlib import Path

import click
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

from line_sleep import LineSleep


class Scraper:
    def __init__(self, email: str, password: str, username: str):
        self.email = email
        self.password = password
        self.username = username

        self.driver = webdriver.Chrome(executable_path=Path("chromedriver").resolve())

        self.image_folder = Path("posts/images")
        self.video_folder = Path("posts/videos")
        self.image_folder.mkdir(parents=True, exist_ok=True)
        self.video_folder.mkdir(parents=True, exist_ok=True)

    def log_into_upvotes_page(self):
        self.driver.get("https://9gag.com")
        self.driver.find_element_by_xpath(
            "/html/body/div[7]/div[1]/div[2]/div/span"
        ).click()  # dismiss cookie warning
        self.driver.find_element_by_xpath(
            "/html/body/header/div/div/div[2]/a[1]"
        ).click()  # login button
        self.driver.find_element_by_xpath(
            "/html/body/div[2]/div[3]/section/section/div/form/div[1]/input"
        ).send_keys(self.email)
        self.driver.find_element_by_xpath(
            "/html/body/div[2]/div[3]/section/section/div/form/div[2]/input"
        ).send_keys(self.password)
        self.driver.find_element_by_xpath(
            "/html/body/div[2]/div[3]/section/section/div/form/div[3]/input"
        ).click()
        self.driver.get(f"https://9gag.com/u/{self.username}/likes")

    def scrape_upvotes(self):
        time.sleep(2)
        body = self.driver.find_element_by_css_selector("body")
        # while True:
        soup = BeautifulSoup(self.driver.page_source, features="html.parser")
        with open("upvotes.html", "w") as f:
            f.write(soup.prettify())
        section_of_posts = soup.find("section", {"id": "list-view-2"})
        image_urls = self.find_img_urls(section_of_posts)
        video_urls = self.find_video_urls(section_of_posts)
        urls_to_scrape = image_urls + video_urls
        with LineSleep(1, __file__, print_=True):
            for _ in range(len(urls_to_scrape)):
                body.send_keys("j")
                # time.sleep(1)  #TODO: try to use LineSleep instead
        for url in urls_to_scrape:
            self.download_from_url(url)

    @staticmethod
    def find_img_urls(section_of_posts):
        images_in_section = section_of_posts.find_all_next(
            "img", alt=True
        )  # only images of posts  have an alt tag
        image_urls = [image["src"] for image in images_in_section]
        full_size_image_urls = []
        for url in image_urls:
            if "460s" in url:
                full_size_image_urls.append(url.replace("460s.jpg", "700b.jpg"))
            elif "460c" in url:
                full_size_image_urls.append(url.replace("460c.jpg", "700b.jpg"))
        return full_size_image_urls

    @staticmethod
    def find_video_urls(section_of_posts):
        videos_in_section = section_of_posts.find_all_next("video")
        video_urls = [video.find("source")["src"] for video in videos_in_section]
        return video_urls

    def download_from_url(self, url: str):
        table = str.maketrans(r"\/", "||")
        filename = url.translate(table)
        if "jpg" in url:
            filename = self.image_folder / filename
        elif "mp4" in url:
            filename = self.video_folder / filename
        else:
            return
        response = requests.get(url)
        with filename.open("wb") as f:
            f.write(response.content)


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
    with LineSleep(1, __file__):
        scraper.log_into_upvotes_page()
    scraper.scrape_upvotes()


if __name__ == "__main__":
    main()
