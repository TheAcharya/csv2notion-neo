import logging
from pathlib import Path

import pytest

from csv2notion.cli import cli, main
from csv2notion.utils_exceptions import CriticalError, NotionError


def test_no_args():
    with pytest.raises(SystemExit):
        cli()


def test_help():
    with pytest.raises(SystemExit):
        cli("--help")


def test_missing_csv():
    with pytest.raises(CriticalError) as e:
        cli("--token", "fake", "fake.csv")

    assert "File fake.csv not found" in str(e.value)


def test_empty_csv(tmp_path):
    test_file = tmp_path / "test.csv"
    test_file.touch()

    with pytest.raises(CriticalError) as e:
        cli("--token", "fake", str(test_file))

    assert "CSV file has no columns" in str(e.value)


def test_no_rows_csv(tmp_path):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,c\n")

    with pytest.raises(CriticalError) as e:
        cli("--token", "fake", str(test_file))

    assert "CSV file is empty" in str(e.value)


@pytest.mark.vcr()
def test_bad_token(tmp_path):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,c\n1,2,3\n")

    with pytest.raises(NotionError) as e:
        cli("--token", "fake", str(test_file))

    assert "Invalid Notion token" in str(e.value)


@pytest.mark.vcr()
def test_bad_url(tmp_path, db_maker):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,c\na,b,c\n")

    with pytest.raises(NotionError) as e:
        cli(
            "--token",
            db_maker.token,
            "--url",
            "https://notnotion.com/bad_url",
            str(test_file),
        )

    assert "Invalid URL" in str(e.value)


@pytest.mark.vcr()
def test_inaccessible_url(tmp_path, db_maker):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,c\na,b,c\n")
    inaccessible_url = (
        "https://www.notion.so/someuser/8e35d9a007b14dd1ae655df9ff6839f3"
        "?v=6f0a1b89496f45209e99ececccd25b7a"
    )

    with pytest.raises(NotionError) as e:
        cli(
            "--token",
            db_maker.token,
            "--url",
            inaccessible_url,
            str(test_file),
        )

    assert "Cannot access" in str(e.value)


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_bad_url_type(tmp_path, db_maker):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,c\na,b,c\n")

    test_db = db_maker.from_csv_head("a,b,c")
    test_row = test_db.add_row({})

    with pytest.raises(NotionError) as e:
        cli(
            "--token",
            db_maker.token,
            "--url",
            test_row.get_browseable_url(),
            str(test_file),
        )

    assert "Provided URL does not point to a Notion database" in str(e.value)


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_read_only_url(tmp_path, db_maker):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,c\na,b,c\n")

    read_only_url = (
        "https://www.notion.so/vzhd1701/70ffd895eb1947b18bda9dacf535f67f?"
        "v=c081db7615274caa9d90e6e8609fcda8"
    )

    with pytest.raises(NotionError) as e:
        cli(
            "--token",
            db_maker.token,
            "--url",
            read_only_url,
            str(test_file),
        )

    assert "You must have editing permissions for Notion database" in str(e.value)


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_new_page(tmp_path, db_maker):
    test_file = tmp_path / f"{db_maker.page_name}.csv"
    test_file.write_text("a,b,c\na,b,c\n")

    test_db = db_maker.from_cli("--token", db_maker.token, str(test_file))

    assert test_db.page.title == db_maker.page_name
    assert test_db.page.type == "collection_view_page"

    assert test_db.header == {"a", "b", "c"}
    assert len(test_db.rows) == 1
    assert test_db.rows[0].columns["a"] == "a"
    assert test_db.rows[0].columns["b"] == "b"
    assert test_db.rows[0].columns["c"] == "c"


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_new_page_empty_rows(tmp_path, db_maker):
    test_file = tmp_path / f"{db_maker.page_name}.csv"
    test_file.write_text("a,b,c\n\n\n,\n\n\n,,")

    test_db = db_maker.from_cli(
        "--token", db_maker.token, "--max-threads=1", str(test_file)
    )

    assert test_db.header == {"a", "b", "c"}
    assert len(test_db.rows) == 2
    assert test_db.rows[0].columns["a"] == ""
    assert test_db.rows[0].columns["b"] == ""
    assert test_db.rows[0].columns["c"] == ""
    assert test_db.rows[1].columns["a"] == ""
    assert test_db.rows[1].columns["b"] == ""
    assert test_db.rows[1].columns["c"] == ""


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_new_page_column_order(tmp_path, db_maker):
    test_file = tmp_path / f"{db_maker.page_name}.csv"
    test_file.write_text("c,b,a\nc,b,a\n")

    test_db = db_maker.from_cli("--token", db_maker.token, str(test_file))

    table_view_header = test_db.default_view_header

    assert test_db.page.title == db_maker.page_name
    assert test_db.page.type == "collection_view_page"

    assert table_view_header == ["c", "b", "a"]
    assert len(test_db.rows) == 1
    assert test_db.rows[0].columns["a"] == "a"
    assert test_db.rows[0].columns["b"] == "b"
    assert test_db.rows[0].columns["c"] == "c"


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_existing_page(tmp_path, db_maker):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,c\naa,bb,cc\n")

    test_db = db_maker.from_csv_head("a,b,c")

    cli(
        "--token",
        db_maker.token,
        "--url",
        test_db.url,
        str(test_file),
    )

    assert test_db.header == {"a", "b", "c"}
    assert len(test_db.rows) == 1
    assert test_db.rows[0].columns["a"] == "aa"
    assert test_db.rows[0].columns["b"] == "bb"
    assert test_db.rows[0].columns["c"] == "cc"


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_inconsistent_columns_csv(tmp_path, db_maker, caplog):
    test_file = tmp_path / f"{db_maker.page_name}.csv"
    test_file.write_text("a,b\na,b,c\n")

    with caplog.at_level(logging.WARNING, logger="csv2notion"):
        test_db = db_maker.from_cli("--token", db_maker.token, str(test_file))

    assert test_db.header == {"a", "b"}
    assert len(test_db.rows) == 1
    assert test_db.rows[0].columns["a"] == "a"
    assert test_db.rows[0].columns["b"] == "b"

    assert "Inconsistent number of columns detected" in caplog.text


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_existing_page_column_mismatch(tmp_path, db_maker):
    test_file = tmp_path / "test.csv"
    test_file.write_text("a,b,c\naa,bb,cc\n")

    test_db = db_maker.from_csv_head("d,e")

    with pytest.raises(NotionError) as e:
        cli(
            "--token",
            db_maker.token,
            "--url",
            test_db.url,
            str(test_file),
        )

    assert "No columns left after validation, nothing to upload" in str(e.value)


def test_log_file(fs, mocker):
    mocker.patch(
        "sys.argv",
        ["csv2notion", "--token", "fake", "--log", "test_log.txt", "fake_file.csv"],
    )

    with pytest.raises(SystemExit) as e:
        main()

    log_txt = Path("test_log.txt").read_text("utf-8")

    assert e.value.code == 1
    assert "File fake_file.csv not found" in log_txt


def test_keyboard_interrupt(mocker):
    mocker.patch("csv2notion.cli.cli", side_effect=KeyboardInterrupt)

    with pytest.raises(SystemExit) as e:
        main()

    assert e.value.code == 1


def test_main_import():
    from csv2notion import __main__  # noqa: F401, WPS433
