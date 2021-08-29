import click

from scraper import Scraper


def prompt_proxy(ctx, b):
    print(ctx, b)
    username = ctx.params.get("username")
    if not username:
        username = click.prompt("Your 9GAG username", type=str)

    email = ctx.params.get("email")
    if not email:
        email = click.prompt("Your 9GAG Facebook/Google/9GAG email adress", type=str)

    password = ctx.params.get("password")
    if not password:
        password = click.prompt("Your 9GAG account password", hide_input=True)

    return {
        "username": username,
        "email": email,
        "password": password,
    }


@click.command()
@click.option("-u", "--username", is_eager=True, type=str)
@click.option("-e", "--email", is_eager=True, help="Your 9gag account email", type=str)
@click.option(
    "-p",
    "--password",
    is_eager=True,
    help="Your 9gag account password",
    type=str,
)
def main(username, email, password):
    scraper = Scraper(email, password, username)
    scraper.scrape_upvotes()


if __name__ == "__main__":
    main()
