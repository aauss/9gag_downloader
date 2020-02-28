import time
from pathlib import Path

import click
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from line_sleep import LineSleep


class Scraper:
    def __init__(self, account_type: str, email: str, password: str, username: str):
        self.account_type = account_type
        self.email = email
        self.password = password
        self.username = username

        self.driver = webdriver.Chrome(executable_path=Path("../chromedriver").resolve())

        self.image_folder = Path(f"../{self.username}_posts/images")
        self.video_folder = Path(f"../{self.username}_posts/videos")
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
        if self.account_type == "own email":
            self.log_in_with_own_email()
        elif self.account_type == "google":
            self.log_in_with_google()
        self.driver.get(f"https://9gag.com/u/{self.username}/likes")

    def log_in_with_own_email(self):
        self.driver.find_element_by_xpath(
            "/html/body/div[2]/div[3]/section/section/div/form/div[1]/input"
        ).send_keys(self.email)
        self.driver.find_element_by_xpath(
            "/html/body/div[2]/div[3]/section/section/div/form/div[2]/input"
        ).send_keys(self.password)
        self.driver.find_element_by_xpath(
            "/html/body/div[2]/div[3]/section/section/div/form/div[3]/input"
        ).click()  # login button

    def log_in_with_google(self):
        self.driver.get("https://9gag.com/connect/google?next=%2F")
        self.driver.find_element_by_xpath("""//*[@id="identifierId"]""").send_keys(
            self.email + Keys.ENTER
        )
        self.driver.find_element_by_xpath(
            """//*[@id="password"]/div[1]/div/div[1]/input"""
        ).send_keys(self.password + Keys.ENTER)

    def scrape_upvotes(self):
        urls_to_scrape = []
        try:
            body = self.driver.find_element_by_css_selector("body")
            soup = BeautifulSoup(
                body.get_attribute("innerHTML"), features="html.parser"
            )
            section_of_posts = soup.find("section", {"id": "list-view-2"})
            image_urls = self.find_img_urls(section_of_posts)
            video_urls = self.find_video_urls(section_of_posts)
            urls_to_scrape = image_urls + video_urls
        except Exception as e:
            print(e)
        finally:
            with Path("urls.txt").open("w") as f:
                f.write(" ".join(urls_to_scrape))

    def scroll_until_end(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            # Wait to load page
            time.sleep(1.5)
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    @staticmethod
    def find_img_urls(section_of_posts):
        images_in_section = section_of_posts.find_all_next(
            "img", alt=True
        )  # only images of posts have an alt tag
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
        video_urls = [
            video.find("source", {"type": "video/mp4"})["src"]
            for video in videos_in_section
        ]
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
@click.option(
    "-t",
    "--account-type",
    help="do you use social media or your own email address to log in?",
    type=click.Choice(["google", "own email"], case_sensitive=False),
    prompt=True,
)
@click.option("-e", "--email", help="your 9gag account email", type=str, prompt=True)
@click.option(
    "-p",
    "--password",
    help="your 9gag account password",
    type=str,
    prompt=True,
    hide_input=True,
)
@click.option("-u", "--username", help="your 9gag username", type=str, prompt=True)
def main(
    account_type, email, password, username,
):
    scraper = Scraper(account_type, email, password, username)
    with LineSleep(2.5, __file__):
        scraper.log_into_upvotes_page()
    scraper.scroll_until_end()


if __name__ == "__main__":
    main()
