import click

from scraper import Scraper


@click.command()
@click.option("-u", "--username", help="Your 9gag username", type=str, prompt=True)
@click.option(
    "-e",
    "--email",
    help="Your 9gag account email",
    type=str,
    prompt=True,
)
@click.option(
    "-p",
    "--password",
    help="Your 9gag account password",
    type=str,
    prompt=True,
    hide_input=True,
)
def main(username, email, password):
    scraper = Scraper(email, password, username)
    scraper.scrape_upvotes()


if __name__ == "__main__":
    main()
