"""
NetGuard - Report Generator Module
Exports scan/discovery/banner/arp results to JSON or HTML files.
"""

import csv
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


def _csv_safe(value):
    """
    Neutralize spreadsheet formulas in untrusted text (CSV injection).
    Banners come from remote hosts, so a value like =HYPERLINK(...) must
    not be executed when the file is opened in Excel.
    """
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + value
    return value


def _flatten(data: dict):
    """
    Turn a results dict into (headers, rows) for tabular output.
    Plain fields repeat on every row. The first list field expands into one
    row per item (dict items add one column per key). Any further list
    fields are joined into a single cell.
    """
    list_key = next((k for k, v in data.items() if isinstance(v, list)), None)
    scalars = {
        k: (", ".join(str(x) for x in v) if isinstance(v, list) else v)
        for k, v in data.items()
        if k != list_key
    }
    if list_key is None:
        return list(scalars), [list(scalars.values())]

    items = data[list_key]
    if items and all(isinstance(i, dict) for i in items):
        columns = list(items[0].keys())
        rows = [list(scalars.values()) + [i.get(c, "") for c in columns] for i in items]
        return list(scalars) + columns, rows

    rows = [list(scalars.values()) + [i] for i in items]
    return list(scalars) + [list_key], rows


def generate_csv_report(data: dict, filepath: str):
    """
    Write a results dict to a CSV file (one row per result). Saved as
    UTF-8 with a BOM so Excel on Windows opens it correctly.
    """
    headers, rows = _flatten(data)
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in rows:
            writer.writerow([_csv_safe(v) for v in row])
    print(f"[*] CSV report saved to {filepath}")


def _md_cell(value) -> str:
    """Make a value safe to place inside a Markdown table cell."""
    if isinstance(value, dict):
        value = ", ".join(f"{k}: {v}" for k, v in value.items())
    text = html.escape(str(value), quote=False)
    text = text.replace("\\", "\\\\").replace("|", "\\|")
    return text.replace("\r\n", "<br>").replace("\n", "<br>").replace("\r", "<br>")


def generate_markdown_report(data: dict, filepath: str):
    """
    Write a results dict to a Markdown file with a Field/Value table,
    ready to paste into a README, issue, or write-up.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# NetGuard Report",
        "",
        f"Generated: {timestamp}",
        "",
        "| Field | Value |",
        "|-------|-------|",
    ]
    for key, value in data.items():
        if isinstance(value, list):
            cell = "<br>".join(_md_cell(v) for v in value) if value else "(none)"
        else:
            cell = _md_cell(value)
        lines.append(f"| {_md_cell(key)} | {cell} |")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[*] Markdown report saved to {filepath}")


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
