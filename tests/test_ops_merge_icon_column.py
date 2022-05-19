import logging
import re

import pytest

from csv2notion.cli import cli


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_merge_icon_column_with_content(tmp_path, db_maker, caplog):
    test_icon_url1 = "https://via.placeholder.com/100"
    test_icon_url2 = "https://via.placeholder.com/200"

    test_file = tmp_path / f"{db_maker.page_name}.csv"
    test_file.write_text(f"a,b,icon url\na,b,{test_icon_url1}\n")

    with caplog.at_level(logging.INFO, logger="csv2notion"):
        cli(
            [
                "--token",
                db_maker.token,
                "--icon-column",
                "icon url",
                str(test_file),
            ]
        )

    url = re.search(r"New database URL: (.*)$", caplog.text, re.M)[1]

    test_db = db_maker.from_url(url)

    test_file.write_text(f"a,b,icon url\na,b,{test_icon_url2}\n")

    cli(
        [
            "--token",
            db_maker.token,
            "--url",
            test_db.url,
            "--merge",
            "--icon-column",
            "icon url",
            str(test_file),
        ]
    )

    table_rows = test_db.rows
    table_header = test_db.header

    assert table_header == {"a", "b"}
    assert len(table_rows) == 1

    assert getattr(table_rows[0].columns, "a") == "a"
    assert getattr(table_rows[0].columns, "b") == "b"
    assert len(table_rows[0].children) == 0
    assert table_rows[0].icon == test_icon_url2


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_merge_icon_column_with_content_no_reupload(
    tmp_path, db_maker, smallest_gif, caplog
):
    test_icon1 = tmp_path / "test_icon1.gif"
    test_icon1.write_bytes(smallest_gif)

    test_icon2 = tmp_path / "test_icon2.gif"
    test_icon2.write_bytes(smallest_gif)

    test_file = tmp_path / f"{db_maker.page_name}.csv"
    test_file.write_text(f"a,b,icon file\na,b,{test_icon1.name}")

    with caplog.at_level(logging.INFO, logger="csv2notion"):
        cli(
            [
                "--token",
                db_maker.token,
                "--icon-column",
                "icon file",
                str(test_file),
            ]
        )

    url = re.search(r"New database URL: (.*)$", caplog.text, re.M)[1]

    test_db = db_maker.from_url(url)
    icon_meta_pre = test_db.rows[0].get("properties.icon_meta", force_refresh=True)

    test_file.write_text(f"a,b,icon file\na,b,{test_icon2}\n")

    cli(
        [
            "--token",
            db_maker.token,
            "--url",
            test_db.url,
            "--merge",
            "--icon-column",
            "icon file",
            str(test_file),
        ]
    )

    table_rows = test_db.rows
    table_header = test_db.header

    icon_meta_after = test_db.rows[0].get("properties.icon_meta", force_refresh=True)

    assert table_header == {"a", "b"}
    assert len(table_rows) == 1

    assert getattr(table_rows[0].columns, "a") == "a"
    assert getattr(table_rows[0].columns, "b") == "b"
    assert len(table_rows[0].children) == 0
    assert icon_meta_pre == icon_meta_after


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_merge_icon_column_url_to_file(tmp_path, db_maker, smallest_gif, caplog):
    test_icon_url = "https://via.placeholder.com/100"

    test_icon_file = tmp_path / "test_icon_file.gif"
    test_icon_file.write_bytes(smallest_gif)

    test_file = tmp_path / f"{db_maker.page_name}.csv"
    test_file.write_text(f"a,b,icon url\na,b,{test_icon_url}")

    with caplog.at_level(logging.INFO, logger="csv2notion"):
        cli(
            [
                "--token",
                db_maker.token,
                "--icon-column",
                "icon url",
                str(test_file),
            ]
        )

    url = re.search(r"New database URL: (.*)$", caplog.text, re.M)[1]

    test_db = db_maker.from_url(url)

    test_file.write_text(f"a,b,icon file\na,b,{test_icon_file}\n")

    cli(
        [
            "--token",
            db_maker.token,
            "--url",
            test_db.url,
            "--merge",
            "--icon-column",
            "icon file",
            str(test_file),
        ]
    )

    table_rows = test_db.rows
    table_header = test_db.header

    assert table_header == {"a", "b"}
    assert len(table_rows) == 1

    assert getattr(table_rows[0].columns, "a") == "a"
    assert getattr(table_rows[0].columns, "b") == "b"
    assert len(table_rows[0].children) == 0
    assert test_icon_file.name in table_rows[0].icon


@pytest.mark.vcr()
@pytest.mark.usefixtures("vcr_uuid4")
def test_merge_icon_column_with_content_reupload_manually_replaced(
    tmp_path, db_maker, smallest_gif, caplog
):
    test_icon1 = tmp_path / "test_icon1.gif"
    test_icon1.write_bytes(smallest_gif)

    test_icon2 = tmp_path / "test_icon2.gif"
    test_icon2.write_bytes(smallest_gif)

    test_file = tmp_path / f"{db_maker.page_name}.csv"
    test_file.write_text(f"a,icon file\na,{test_icon1.name}")

    with caplog.at_level(logging.INFO, logger="csv2notion"):
        cli(
            [
                "--token",
                db_maker.token,
                "--icon-column",
                "icon file",
                str(test_file),
            ]
        )

    url = re.search(r"New database URL: (.*)$", caplog.text, re.M)[1]

    test_db = db_maker.from_url(url)

    test_db.rows[0].icon = "https://via.placeholder.com/100"

    test_file.write_text(f"a,icon file\na,{test_icon2}\n")

    cli(
        [
            "--token",
            db_maker.token,
            "--url",
            test_db.url,
            "--merge",
            "--icon-column",
            "icon file",
            str(test_file),
        ]
    )

    table_rows = test_db.rows
    table_header = test_db.header

    assert table_header == {"a"}
    assert len(table_rows) == 1

    assert getattr(table_rows[0].columns, "a") == "a"
    assert len(table_rows[0].children) == 0
    assert test_icon2.name in table_rows[0].icon
