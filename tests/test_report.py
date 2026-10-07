"""
Unit tests for netguard.report
"""

from netguard.report import generate_html_report


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
