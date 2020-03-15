import logging
import time
from pathlib import Path

import click
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from downloader.line_sleep import LineSleep

WAIT = 10


class Scraper:
    def __init__(self, account_type: str, email: str, password: str, username: str):
        self.account_type = account_type
        self.email = email
        self.password = password
        self.username = username

        self.driver = webdriver.Chrome(
            executable_path=(Path(__file__).parent.parent / "chromedriver").resolve()
        )
        self.image_folder = Path(f"../{self.username}_posts/images")
        self.video_folder = Path(f"../{self.username}_posts/videos")
        self.image_folder.mkdir(parents=True, exist_ok=True)
        self.video_folder.mkdir(parents=True, exist_ok=True)

    def log_into_upvotes_page(self):
        self.dismiss_cookie_warning()
        self.click_login_button()
        if self.account_type == "own email":
            self.log_in_with_own_email()
        elif self.account_type == "google":
            self.log_in_with_google()
        self.driver.get(f"https://9gag.com/u/{self.username}/likes")

    def dismiss_cookie_warning(self):
        self.driver.get("https://9gag.com")
        try:
            cookie_warning_x_button = "/html/body/div[7]/div[1]/div[2]/div/span"
            cookie_warning = WebDriverWait(self.driver, WAIT).until(
                EC.element_to_be_clickable((By.XPATH, cookie_warning_x_button))
            )
            cookie_warning.click()
        except TimeoutException:
            logging.exception("Cookie warning could not be dismissed.")

    def click_login_button(self):
        login_button = "/html/body/header/div/div/div[2]/a[1]"
        login_button = WebDriverWait(self.driver, WAIT).until(
            EC.element_to_be_clickable((By.XPATH, login_button))
        )
        login_button.click()

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
        except Exception as error:
            print(error)
        finally:
            with Path("urls.txt").open("w") as file_:
                file_.write(" ".join(urls_to_scrape))

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
        with filename.open("wb") as file_:
            file_.write(response.content)


def prompt_proxy(ctx, _, public):
    username = ctx.params.get("username")
    if not username:
        username = click.prompt("Your 9GAG username", type=str)
    if public:
        return {"public": True, "username": username}
    account_type = ctx.params.get("account_type")
    if not account_type:
        account_type = click.prompt(
            "Do you use Google or classic email to log in?",
            type=click.Choice(["google", "classic"], case_sensitive=False),
        )

    email = ctx.params.get("email")
    if not email:
        email = click.prompt("Your 9GAG Facebook/Google/9GAG email adress", type=str)

    password = ctx.params.get("password")
    if not password:
        password = click.prompt("Your 9GAG account password", hide_input=True)

    return {
        "public": False,
        "username": username,
        "account_type": account_type,
        "email": email,
        "password": password,
    }


@click.command()
@click.option("--test", is_flag=True, default=False)
@click.option(
    "--public/--not-public", is_flag=True, default=False, callback=prompt_proxy
)
@click.option("-u", "--username", is_eager=True, type=str)
@click.option(
    "-t",
    "--account-type",
    help="Do you use Google or classic email to log in?",
    type=click.Choice(["google", "classic"], case_sensitive=False),
    is_eager=True,
)
@click.option("-e", "--email", is_eager=True, help="Your 9gag account email", type=str)
@click.option(
    "-p", "--password", is_eager=True, help="Your 9gag account password", type=str,
)
def main(public, username, account_type, email, password, test):
    if test:
        click.echo(public)
    else:
        scraper = Scraper(account_type, email, password, username)
        with LineSleep(2.5, __file__):
            scraper.log_into_upvotes_page()
        scraper.scroll_until_end()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
