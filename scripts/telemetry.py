"""Render public GitHub portfolio telemetry; no third-party Python packages."""
import argparse
import collections
import datetime as dt
import html
import json
import math
import os
from pathlib import Path
import tempfile
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
USER = "DanoV1m"
API = "https://api.github.com"
NAMES = ("github-stats", "top-languages", "contribution-3d", "contribution-snake")
COLORS = ("#16283C", "#164E63", "#0369A1", "#2563EB", "#38BDF8")


def request(path, token, payload=None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "DanoV1m-profile"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = None if payload is None else json.dumps(payload).encode()
    if data is not None:
        headers["Content-Type"] = "application/json"
    with urllib.request.urlopen(urllib.request.Request(API + path, data=data, headers=headers), timeout=30) as response:
        return json.load(response)


def get_data(token):
    repos = []
    page = 1
    while True:
        batch = request(f"/users/{USER}/repos?type=owner&per_page=100&page={page}", token)
        if not isinstance(batch, list):
            raise ValueError("Unexpected repository response")
        repos.extend(r for r in batch if r.get("private") is False and r.get("fork") is False
                     and r["owner"]["login"].lower() == USER.lower())
        if len(batch) < 100:
            break
        page += 1
    langs = collections.Counter()
    for repo in repos:
        name = urllib.parse.quote(repo["name"], safe="")
        langs.update(request(f"/repos/{USER}/{name}/languages", token))
    query = """query($login:String!) { user(login:$login) { contributionsCollection {
      contributionCalendar { totalContributions weeks { contributionDays { date weekday contributionCount } } }
    } } }"""
    response = request("/graphql", token, {"query": query, "variables": {"login": USER}})
    if response.get("errors") or not response.get("data", {}).get("user"):
        raise RuntimeError("GitHub contribution calendar query failed")
    calendar = response["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return {"repos": len(repos), "stars": sum(r["stargazers_count"] for r in repos),
            "forks": sum(r["forks_count"] for r in repos), "langs": dict(langs),
            "calendar": calendar}


def text(x, y, label, size=16, color="#E2E8F0", weight="normal"):
    return f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}">{html.escape(str(label))}</text>'


def svg(title, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{h}" viewBox="0 0 900 {h}" role="img">'
            f'<title>{html.escape(title)}</title><rect x="1" y="1" width="898" height="{h-2}" rx="14" fill="#0D1828" stroke="#284764" stroke-width="2"/>'
            + body + '</svg>\n')


def render(data, date):
    weeks = data["calendar"]["weeks"]
    if not 1 <= len(weeks) <= 54:
        raise ValueError("Unexpected number of contribution weeks")
    days = [(i, d["weekday"], d["contributionCount"]) for i, w in enumerate(weeks) for d in w["contributionDays"]]
    if not days or any(not isinstance(n, int) or n < 0 or not 0 <= r <= 6 for _, r, n in days):
        raise ValueError("Invalid calendar")
    for w in weeks:
        for d in w["contributionDays"]:
            dt.date.fromisoformat(d["date"])
    if len(set((c, r) for c, r, _ in days)) != len(days):
        raise ValueError("Duplicate calendar cell")
    maximum = max(1, max(n for _, _, n in days))
    color = lambda n: COLORS[0 if n == 0 else min(4, 1 + int(3 * math.log1p(n) / math.log1p(maximum)))]
    stamp = f"Updated {date} UTC"
    stats = text(22, 30, "PUBLIC REPOSITORY TELEMETRY", 16, "#38BDF8", "bold")
    for i, (label, value) in enumerate([("Repositories", data["repos"]), ("Stars", data["stars"]), ("Forks", data["forks"]), ("Calendar contributions", data["calendar"]["totalContributions"])]):
        x = 22 + i * 220
        stats += text(x, 69, value, 27, "#F1F5F9", "bold") + text(x, 91, label, 12, "#94A3B8")
    stats += text(22, 119, stamp, 11, "#94A3B8")
    items = sorted(((k, v) for k, v in data["langs"].items() if v > 0), key=lambda x: (-x[1], x[0]))
    total = sum(v for _, v in items)
    lang = text(22, 30, "PUBLIC REPOSITORY LANGUAGES / BYTES", 16, "#38BDF8", "bold")
    if total:
        top = items[:7]
        if len(items) > 7:
            top.append(("Other", sum(v for _, v in items[7:])))
        x = 22.0
        palette = ["#38BDF8","#2563EB","#60A5FA","#0891B2","#818CF8","#94A3B8","#0E7490","#64748B"]
        for i, (name, value) in enumerate(top):
            width = 856 * value / total
            lang += f'<rect x="{x:.3f}" y="44" width="{width:.3f}" height="12" fill="{palette[i]}"/>'
            x += width
            lx, ly = 22 + i % 4 * 215, 82 + i // 4 * 25
            lang += f'<circle cx="{lx+4}" cy="{ly-4}" r="4" fill="{palette[i]}"/>'
            lang += text(lx+13, ly, f"{name[:18]} {100*value/total:.1f}%", 13)
    else:
        lang += text(22, 80, "No language bytes reported.", 14)
    lang += text(22, 131, stamp + " · Composition, not proficiency", 11, "#94A3B8")
    iso = text(22, 30, "3D CONTRIBUTION LANDSCAPE", 16, "#38BDF8", "bold")
    for c, r, n in sorted(days, key=lambda d: (d[0], -d[1])):
        x, y = 32 + c * 14 + (6-r) * 9, 113 + c * 1.2 - (6-r) * 4.7
        height = 0 if n == 0 else 4 + 58 * math.log1p(n) / math.log1p(maximum)
        t = y-height
        iso += f'<g><title>{n} contributions</title><path d="M{x},{t} l7,-3 7,3 -7,3 Z" fill="{color(n)}"/>'
        if height:
            iso += f'<path d="M{x},{t} l7,3 v{height} l-7,-3 Z" fill="#164E63"/><path d="M{x+7},{t+3} l7,-3 v{height} l-7,3 Z" fill="#075985"/>'
        iso += '</g>'
    iso += text(22, 205, stamp + " · Height is logarithmic · One tile per day", 11, "#94A3B8")
    snake = text(22, 30, "CONTRIBUTION SNAKE / ANIMATED SWEEP", 16, "#38BDF8", "bold")
    for c, r, n in days:
        snake += f'<rect x="{22+c*16}" y="{44+r*16}" width="13" height="13" rx="2" fill="{color(n)}"><title>{n} contributions</title></rect>'
    points = [(22+c*16+6.5, 44+r*16+6.5) for c,r,n in sorted(days, key=lambda d: (d[1], d[0] if d[1]%2==0 else -d[0]))]
    path = "M" + " L".join(f"{x},{y}" for x,y in points)
    snake += f'<path id="route" d="{path}" fill="none" stroke="#67E8F9" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" pathLength="100" stroke-dasharray="5 95" stroke-dashoffset="5"><animate attributeName="stroke-dashoffset" values="5;-100" dur="25s" repeatCount="indefinite"/></path>'
    snake += text(22, 174, stamp + " · Animated path over actual contribution cells", 11, "#94A3B8")
    return dict(zip(NAMES, [svg("Public repository statistics", 138, stats), svg("Public languages", 148, lang), svg("Contribution landscape", 223, iso), svg("Contribution snake", 190, snake)]))


def check_assets(root):
    for file in list((root/"assets").rglob("*.svg")) + list((root/"generated").glob("*.svg")):
        tree = ET.parse(file)
        assert tree.getroot().tag == "{http://www.w3.org/2000/svg}svg", file
        for element in tree.iter():
            assert not element.tag.endswith("script"), file
            assert not any(a.lower().startswith("on") for a in element.attrib), file
    import re
    readme = (root/"README.md").read_text()
    for path in re.findall(r'src="((?:assets|generated)/[^"]+)"', readme):
        assert (root/path).is_file(), path
    assert "volteach" not in readme.lower(), "Pending security review"
    assert "spotify-pending.svg" in readme


def self_test():
    fixture = {"repos": 2, "stars": 0, "forks": 1, "langs": {"C++": 40, "Test & More": 60},
               "calendar": {"totalContributions": 7, "weeks": [{"contributionDays": [{"weekday": 0,"date":"2026-01-04","contributionCount":0},{"weekday":1,"date":"2026-01-05","contributionCount":7}]}]}}
    outputs = render(fixture, "2026-01-05")
    assert set(outputs) == set(NAMES)
    for content in outputs.values():
        ET.fromstring(content)
        assert "2026-01-05" in content
    assert "Test &amp; More" in outputs["top-languages"]
    assert "60.0%" in outputs["top-languages"]
    assert "<animate" in outputs["contribution-snake"]
    fixture["langs"] = {}
    assert "No language bytes" in render(fixture, "2026-01-05")["top-languages"]
    fixture["calendar"]["weeks"] = []
    try:
        render(fixture, "2026-01-05")
    except ValueError:
        pass
    else:
        raise AssertionError("Empty calendar accepted")
    check_assets(ROOT)
    print("Offline telemetry fixtures, SVG XML and local README image references passed.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    if args.test:
        self_test()
        return
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("GH_TOKEN is required; no data was changed.")
    data = get_data(token)
    outputs = render(data, dt.datetime.now(dt.timezone.utc).date().isoformat())
    for content in outputs.values():
        ET.fromstring(content)
    target = ROOT / "generated"
    target.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target) as folder:
        for name, content in outputs.items():
            (Path(folder)/f"{name}.svg").write_text(content, encoding="utf-8")
        for name in outputs:
            (Path(folder)/f"{name}.svg").replace(target/f"{name}.svg")
    print("Rendered four telemetry assets.")


if __name__ == "__main__":
    main()
