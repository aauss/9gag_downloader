import shutil
from pathlib import Path

import pytest

from downloader.main import Scraper


@pytest.fixture(scope="module")
def scraper_instance():
    scraper_instance = Scraper(
        account_type="own email",
        email="fake@fake.com",
        password="weak_pw",
        username="test_user",
    )
    scraper_instance.driver.get("https://9gag.com")
    yield scraper_instance
    scraper_instance.driver.close()


def test_scraper_folder(scraper_instance: Scraper):
    path = Path(f"../{scraper_instance.username}_posts")
    assert path.is_dir()
    assert (path / "videos").is_dir()
    assert (path / "images").is_dir()
    shutil.rmtree(path)


def test_dismiss_cookie_warning(scraper_instance: Scraper):
    scraper_instance.dismiss_cookie_warning()


def test_click_login_button(scraper_instance: Scraper):
    scraper_instance.click_login_button()


def test_email_login(scraper_instance: Scraper):
    scraper_instance.log_in_with_own_email()
