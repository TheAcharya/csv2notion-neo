import logging
from pathlib import Path

import pytest

from csv2notion_neo.cli import cli, main
from csv2notion_neo.utils_exceptions import CriticalError, NotionError


def test_no_args():
    with pytest.raises(SystemExit):
        cli()


def test_help():
    with pytest.raises(SystemExit):
        cli("--help")


def test_missing_csv():
    with pytest.raises(CriticalError) as e:
        cli("--workspace","Arjun's notion","--token", "fake", "fake.csv")

    assert "File fake.csv not found" in str(e.value)


def test_empty_csv(tmp_path):
    test_file = tmp_path / "test.csv"
    test_file.touch()

    with pytest.raises(CriticalError) as e:
        cli("--workspace","Arjun's notion","--token", "fake", str(test_file))

    assert "CSV file has no columns" in str(e.value)


def test_no_rows_csv(tmp_path):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,c\n")

    with pytest.raises(CriticalError) as e:
        cli("--workspace","Arjun's notion","--token", "fake", str(test_file))

    assert "csv file is empty" in str(e.value)


@pytest.mark.vcr()
def test_bad_token(tmp_path):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,c\n1,2,3\n")

    with pytest.raises(NotionError) as e:
        cli("--workspace","Arjun's notion","--token", "fake", str(test_file))

    assert "Invalid Notion token" in str(e.value)


def test_log_file(fs, mocker):
    mocker.patch(
        "sys.argv",
        ["csv2notion_neo","--workspace","arjun", "--token", "fake", "--log", "test_log.txt", "fake_file.csv"],
    )

    with pytest.raises(SystemExit) as e:
        main()

    log_txt = Path("test_log.txt").read_text("utf-8")

    assert e.value.code == 1
    assert "File fake_file.csv not found" in log_txt


def test_keyboard_interrupt(mocker):
    mocker.patch("csv2notion_neo.cli.cli", side_effect=KeyboardInterrupt)

    with pytest.raises(SystemExit) as e:
        main()

    assert e.value.code == 1


def test_main_import():
    from csv2notion_neo import __main__  # noqa: F401, WPS433
