from click.testing import CliRunner

from downloader.main import main


def test_options():
    runner = CliRunner()
    result = runner.invoke(
        main, "-t google -u user -e some@email.com -p passwort123 --test"
    )
    assert result.exit_code == 0
    assert (
        result.output == "{'public': False, "
        "'username': 'user', "
        "'account_type': 'google', "
        "'email': 'some@email.com', "
        "'password': 'passwort123'}\n"
    )


def test_input_email():
    runner = CliRunner()
    result = runner.invoke(
        main, "-t google -u user -p passwort123 --test", input="some@email.com\n"
    )
    assert result.exit_code == 0
    assert (
        result.output == "Your 9GAG Facebook/Google/9GAG email adress: some@email.com\n"
        "{'public': False, "
        "'username': 'user', "
        "'account_type': 'google', "
        "'email': 'some@email.com', "
        "'password': 'passwort123'}\n"
    )


def test_input_user():
    runner = CliRunner()
    result = runner.invoke(
        main, "-t google -e some@email.com -p passwort123 --test", input="user\n"
    )
    assert result.exit_code == 0
    assert (
        result.output == "Your 9GAG username: user\n"
        "{'public': False, "
        "'username': 'user', "
        "'account_type': 'google', "
        "'email': 'some@email.com', "
        "'password': 'passwort123'}\n"
    )


def test_input_type():
    runner = CliRunner()
    result = runner.invoke(
        main, "-u user -e some@email.com -p passwort123 --test", input="google\n"
    )
    assert result.exit_code == 0
    assert (
        result.output
        == "Do you use Google or classic email to log in? (google, classic): google\n"
        "{'public': False, "
        "'username': 'user', "
        "'account_type': 'google', "
        "'email': 'some@email.com', "
        "'password': 'passwort123'}\n"
    )


def test_input_password():
    runner = CliRunner()
    result = runner.invoke(
        main, "-u user -t google -e some@email.com  --test", input="passwort123\n"
    )
    assert result.exit_code == 0
    assert (
        result.output == "Your 9GAG account password: \n"
        "{'public': False, "
        "'username': 'user', "
        "'account_type': 'google', "
        "'email': 'some@email.com', "
        "'password': 'passwort123'}\n"
    )
