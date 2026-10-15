"""
End-to-end checks that --format csv / md write real files from the CLI.
"""

from tests.test_cli_config import run_cli


def test_scan_can_write_a_csv_report(tmp_path):
    result = run_cli(tmp_path, "scan", "127.0.0.1", "--top-ports", "3",
                     "-o", "out.csv", "-f", "csv")
    assert result.returncode == 0
    first_line = (tmp_path / "out.csv").read_text(encoding="utf-8-sig").splitlines()[0]
    assert first_line == "target,open_ports"


def test_scan_can_write_a_markdown_report(tmp_path):
    result = run_cli(tmp_path, "scan", "127.0.0.1", "--top-ports", "3",
                     "-o", "out.md", "-f", "md")
    assert result.returncode == 0
    assert "# NetGuard Report" in (tmp_path / "out.md").read_text(encoding="utf-8")


def test_unknown_report_format_is_rejected_by_argparse(tmp_path):
    result = run_cli(tmp_path, "scan", "127.0.0.1", "-o", "out.xml", "-f", "xml")
    assert result.returncode == 2
    assert "invalid choice" in result.stderr
