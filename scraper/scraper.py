import logging
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# from scraper.line_sleep import LineSleep


class Scraper:
    def __init__(self, email: str, password: str, username: str):
        self.email = email
        self.password = password
        self.username = username
        self.driver = webdriver.Chrome(
            executable_path=str(
                (Path(__file__).parent.parent / "chromedriver").resolve()
            )
        )
        self.image_folder = Path(f"{self.username}_posts/images")
        self.video_folder = Path(f"{self.username}_posts/videos")
        self.image_folder.mkdir(parents=True, exist_ok=True)
        self.video_folder.mkdir(parents=True, exist_ok=True)

        self.urls_to_scrape = set()
        self.WAIT = 10

    def scrape_upvotes(self):
        self._go_to_9gag()
        self._log_into_upvotes_page()
        self._find_upvotes_until_end_of_page()
        self._download_upvotes()

    def _go_to_9gag(self):
        self.driver.get("https://9gag.com")
        self._dismiss_cookie_warning()

    def _log_into_upvotes_page(self):
        time.sleep(1.5)                    
        self._click_login_button()
        time.sleep(1.5)
        self._enter_credentials()
        time.sleep(100)
        self._go_to_upvote_page()

    def _dismiss_cookie_warning(self):
        cookie_warning_accept_button = (
            "/html/body/div[1]/div/div/div/div[2]/div/button[2]"
        )
        try:
            cookie_warning = WebDriverWait(self.driver, self.WAIT).until(
                EC.element_to_be_clickable((By.XPATH, cookie_warning_accept_button))
            )
            cookie_warning.click()
        except TimeoutException:
            logging.exception("Cookie warning could not be dismissed.")

    def _click_login_button(self):
        login_button = "/html/body/div[2]/div/header/div/div/div[2]/a[1]"
        try:
            login_button = WebDriverWait(self.driver, self.WAIT).until(
                EC.element_to_be_clickable((By.XPATH, login_button))
            )
            login_button.click()
        except TimeoutError:
            logging.exception("Login button could not be clicked.")

    def _enter_credentials(self):
        self.driver.find_element_by_xpath(
            "/html/body/div[2]/div/div[2]/section/section/div/div[2]/form/div[1]/input"
        ).send_keys(self.email)
        self.driver.find_element_by_xpath(
            "/html/body/div[2]/div/div[2]/section/section/div/div[2]/form/div[2]/input"
        ).send_keys(self.password)
        self.driver.find_element_by_xpath(
            "/html/body/div[2]/div/div[2]/section/section/div/div[2]/form/div[3]"
        ).click()  # login button

    def _go_to_upvote_page(self):
        self.driver.get(f"https://9gag.com/u/{self.username}/likes")

    def _find_upvotes_until_end_of_page(self):
        last_height = self._get_scroll_height()
        while True:
            self._scroll_and_get_upvote_urls()
            new_height = self._get_scroll_height()
            if new_height == last_height:
                # end of page reached
                break
            last_height = new_height

    def _get_scroll_height(self):
        return self.driver.execute_script("return document.body.scrollHeight")

    def _scroll_and_get_upvote_urls(self):
        self._scroll()
        time.sleep(1.5)
        self._scrape_upvotes()

    def _scroll(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def _scrape_upvotes(self):
        try:
            body = self.driver.find_element_by_css_selector("body")
            soup = BeautifulSoup(
                body.get_attribute("innerHTML"), features="html.parser"
            )
            section_of_posts = soup.find("section", {"id": "list-view-2"})
            image_urls = self._find_img_urls(section_of_posts)
            video_urls = self._find_video_urls(section_of_posts)
            self.urls_to_scrape = self.urls_to_scrape.union(image_urls + video_urls)
            print(self.urls_to_scrape)
        except Exception as error:
            print(error)
        finally:
            with Path("urls.txt").open("w") as file_:
                file_.write(" ".join(self.urls_to_scrape))

    def _find_img_urls(self, section_of_posts):
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

    def _find_video_urls(self, section_of_posts):
        videos_in_section = section_of_posts.find_all_next("video")
        video_urls = [
            video.find("source", {"type": "video/mp4"})["src"]
            for video in videos_in_section
        ]
        return video_urls

    def _download_upvotes(self):
        for url in self.urls_to_scrape:
            self._download_from_url(url)

    def _download_from_url(self, url: str):
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
