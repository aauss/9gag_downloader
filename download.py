import click
import os
import time

from selenium import webdriver

from bs4 import BeautifulSoup


class Scraper:
    def __init__(self, email, password, username):
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
        soup = BeautifulSoup(self.driver.page_source, features="html.parser")
        section_of_images = soup.find("section", {"id": "list-view-2"})
        images_in_section = section_of_images.find_all(
            "img", alt=True
        )  # only images of interest have an alt tag
        image_urls = [image["src"] for image in images_in_section]
        full_size_image_urls = [
            url.replace("460s.jpg", "700b.jpg") for url in image_urls
        ]
        for _ in range(len(full_size_image_urls)):
            body.send_keys("j")
            time.sleep(0.7)
            print("scroll")


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
