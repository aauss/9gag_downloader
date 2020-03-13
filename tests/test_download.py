import pytest
import shutil

from pathlib import Path


@pytest.fixture
def scraper_instance():
    from downloader.main import Scraper

    return Scraper(account_type="own email", email="fake@fake.com", password="weak_pw", username="test_user")

def test_scraper_folder(scraper_instance):
    path = Path(f"../{scraper_instance.username}_posts")
    assert path.is_dir()
    assert (path / "videos").is_dir()
    assert (path / "images").is_dir()
    shutil.rmtree(path)


