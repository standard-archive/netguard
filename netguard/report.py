"""
NetGuard - Report Generator Module
Exports scan/discovery/banner/arp results to JSON or HTML files.
"""

import html
import json
from datetime import datetime


def generate_json_report(data: dict, filepath: str):
    """
    Write a results dict to a JSON file with a timestamp and metadata.
    """
    report = {
        "tool": "NetGuard",
        "generated_at": datetime.now().isoformat(),
        "results": data,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[*] JSON report saved to {filepath}")


def generate_html_report(data: dict, filepath: str):
    """
    Write a results dict to a simple, readable HTML file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows = ""
    for key, value in data.items():
        if isinstance(value, list):
            value_html = "<br>".join(html.escape(str(v)) for v in value) if value else "(none)"
        else:
            value_html = html.escape(str(value))
        rows += f"<tr><td>{html.escape(str(key))}</td><td>{value_html}</td></tr>\n"

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>NetGuard Report</title>
<style>
    body {{ font-family: Arial, sans-serif; margin: 40px; background: #0d1117; color: #c9d1d9; }}
    h1 {{ color: #58a6ff; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
    th, td {{ border: 1px solid #30363d; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: #161b22; color: #58a6ff; }}
    tr:nth-child(even) {{ background: #161b22; }}
    .meta {{ color: #8b949e; font-size: 0.9em; }}
</style>
</head>
<body>
    <h1>🛡️ NetGuard Report</h1>
    <p class="meta">Generated: {timestamp}</p>
    <table>
        <tr><th>Field</th><th>Value</th></tr>
        {rows}
    </table>
</body>
</html>
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"[*] HTML report saved to {filepath}")


def generate_report(data: dict, filepath: str, fmt: str = "json"):
    """
    Dispatch to the correct report generator based on format.
    """
    if fmt == "json":
        generate_json_report(data, filepath)
    elif fmt == "html":
        generate_html_report(data, filepath)
    else:
        raise ValueError(f"Unsupported report format: '{fmt}'. Use 'json' or 'html'.")
