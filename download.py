import requests

from bs4 import BeautifulSoup

username = None
likes = requests.get(f"https://9gag.com/u/{username}/likes")
soup = BeautifulSoup(likes.content)
print(soup)
