"""
Unit tests for netguard.report
"""

import csv

import pytest

from netguard.report import (
    generate_csv_report,
    generate_html_report,
    generate_markdown_report,
    generate_report,
)


def test_html_report_escapes_special_characters(tmp_path):
    """
    Values that contain HTML-significant characters (<, >, &) must be
    escaped in the generated report, otherwise they corrupt the HTML
    structure or render incorrectly.
    """
    data = {
        "banner": "<script>alert(1)</script>",
        "note": "A & B",
    }
    filepath = tmp_path / "report.html"
    generate_html_report(data, str(filepath))

    content = filepath.read_text(encoding="utf-8")

    assert "<script>alert(1)</script>" not in content
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in content
    assert "A &amp; B" in content


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.reader(f))


def test_csv_scan_report_has_one_row_per_open_port(tmp_path):
    path = tmp_path / "r.csv"
    generate_csv_report({"target": "127.0.0.1", "open_ports": [22, 80]}, str(path))
    assert read_csv(path) == [
        ["target", "open_ports"],
        ["127.0.0.1", "22"],
        ["127.0.0.1", "80"],
    ]


def test_csv_arp_report_has_one_column_per_device_field(tmp_path):
    data = {
        "target": "192.168.0.0/24",
        "devices": [
            {"ip": "192.168.0.1", "mac": "aa:bb:cc:dd:ee:ff"},
            {"ip": "192.168.0.2", "mac": "11:22:33:44:55:66"},
        ],
    }
    path = tmp_path / "r.csv"
    generate_csv_report(data, str(path))
    assert read_csv(path) == [
        ["target", "ip", "mac"],
        ["192.168.0.0/24", "192.168.0.1", "aa:bb:cc:dd:ee:ff"],
        ["192.168.0.0/24", "192.168.0.2", "11:22:33:44:55:66"],
    ]


def test_csv_banner_report_is_a_single_row(tmp_path):
    data = {"target": "127.0.0.1", "port": 22, "banner": "SSH-2.0-OpenSSH"}
    path = tmp_path / "r.csv"
    generate_csv_report(data, str(path))
    assert read_csv(path) == [
        ["target", "port", "banner"],
        ["127.0.0.1", "22", "SSH-2.0-OpenSSH"],
    ]


def test_csv_empty_results_keep_the_header(tmp_path):
    path = tmp_path / "r.csv"
    generate_csv_report({"target": "10.0.0.0/24", "live_hosts": []}, str(path))
    assert read_csv(path) == [["target", "live_hosts"]]


def test_csv_neutralizes_spreadsheet_formulas(tmp_path):
    data = {"target": "127.0.0.1", "port": 80, "banner": '=HYPERLINK("http://evil","x")'}
    path = tmp_path / "r.csv"
    generate_csv_report(data, str(path))
    assert read_csv(path)[1][2].startswith("'=")


def test_csv_file_starts_with_bom_for_excel(tmp_path):
    path = tmp_path / "r.csv"
    generate_csv_report({"target": "x"}, str(path))
    assert path.read_bytes().startswith(b"\xef\xbb\xbf")


def test_markdown_report_contains_a_field_value_table(tmp_path):
    path = tmp_path / "r.md"
    generate_markdown_report({"target": "127.0.0.1", "open_ports": [22, 80]}, str(path))
    content = path.read_text(encoding="utf-8")
    assert "# NetGuard Report" in content
    assert "| target | 127.0.0.1 |" in content
    assert "| open_ports | 22<br>80 |" in content


def test_markdown_escapes_pipes_html_and_newlines(tmp_path):
    path = tmp_path / "r.md"
    generate_markdown_report({"banner": "a|b <x>\nline2"}, str(path))
    content = path.read_text(encoding="utf-8")
    assert "a\\|b &lt;x&gt;<br>line2" in content


def test_markdown_empty_list_shows_none(tmp_path):
    path = tmp_path / "r.md"
    generate_markdown_report({"live_hosts": []}, str(path))
    assert "| live_hosts | (none) |" in path.read_text(encoding="utf-8")


def test_markdown_formats_device_dicts(tmp_path):
    path = tmp_path / "r.md"
    data = {"devices": [{"ip": "192.168.0.1", "mac": "aa:bb:cc:dd:ee:ff"}]}
    generate_markdown_report(data, str(path))
    assert "ip: 192.168.0.1, mac: aa:bb:cc:dd:ee:ff" in path.read_text(encoding="utf-8")


@pytest.mark.parametrize("fmt", ["json", "html", "csv", "md"])
def test_generate_report_supports_all_formats(tmp_path, fmt):
    path = tmp_path / f"r.{fmt}"
    generate_report({"target": "x"}, str(path), fmt)
    assert path.stat().st_size > 0


def test_generate_report_rejects_unknown_format(tmp_path):
    with pytest.raises(ValueError, match="csv"):
        generate_report({}, str(tmp_path / "r.pdf"), "pdf")
