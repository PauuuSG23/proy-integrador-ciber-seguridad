import os
import json
import requests
from urllib.parse import urljoin, urlparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

# Determine base URL from env
env_target = os.getenv("TARGET_URL") or os.getenv("TARGET_ENDPOINT") or os.getenv("TARGET_BASE")
if not env_target:
    raise SystemExit("Set TARGET_URL or TARGET_BASE environment variable before running this probe.")

parsed = urlparse(env_target)
if parsed.scheme and parsed.netloc:
    base = f"{parsed.scheme}://{parsed.netloc}"
else:
    # assume env_target is just a host
    base = env_target if env_target.startswith("http") else f"https://{env_target}"

# candidate paths to probe
paths = [
    "/",
    "/chat",
    "/api",
    "/api/chat",
    "/api/v1/chat",
    "/chatbot",
    "/api/message",
    "/message",
    "/contact",
    "/contacto",
    "/bot",
    "/bot/chat",
    "/dialog",
    "/v1/chat/completions",
    "/v1/chat",
    "/chat/completion",
    "/conversacion",
]

methods = ["GET", "POST", "OPTIONS"]

# optional headers
headers = {}
headers_env = os.getenv("TARGET_HEADERS")
if headers_env:
    try:
        headers = json.loads(headers_env)
    except Exception:
        headers = {}

results = []

for path in paths:
    url = urljoin(base, path.lstrip('/'))
    for method in methods:
        entry = {
            "url": url,
            "method": method,
            "status_code": None,
            "headers": None,
            "body_snippet": None,
        }
        try:
            if method == "GET":
                resp = requests.get(url, headers=headers, timeout=10)
            elif method == "OPTIONS":
                resp = requests.options(url, headers=headers, timeout=10)
            else:
                # POST
                resp = requests.post(url, json={"message": "probe"}, headers=headers, timeout=10)

            entry["status_code"] = resp.status_code
            entry["headers"] = dict(resp.headers)
            text = resp.text
            entry["body_snippet"] = text[:1000]

        except Exception as e:
            entry["status_code"] = "error"
            entry["headers"] = {}
            entry["body_snippet"] = str(e)

        results.append(entry)

now = datetime.now().strftime("%Y%m%d_%H%M%S")
json_path = REPORTS_DIR / f"probe_report_{now}.json"
html_path = REPORTS_DIR / f"probe_report_{now}.html"

with open(json_path, "w", encoding="utf-8") as f:
    json.dump({"base": base, "results": results}, f, indent=2, ensure_ascii=False)

# simple HTML summary
rows = ""
for r in results:
    rows += f"<tr><td>{r['method']}</td><td>{r['url']}</td><td>{r['status_code']}</td><td><pre>{(r['body_snippet'] or '')}</pre></td></tr>\n"

html = f"""
<!doctype html>
<html>
<head><meta charset='utf-8'><title>Probe Report {now}</title></head>
<body>
<h1>Probe Report</h1>
<p>Base: {base}</p>
<table border='1' style='width:100%;border-collapse:collapse;'>
<thead><tr><th>Method</th><th>URL</th><th>Status</th><th>Body (snippet)</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Probe JSON: {json_path}")
print(f"Probe HTML: {html_path}")
