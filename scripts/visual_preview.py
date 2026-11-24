"""Browser smoke check of the README image layout, not GitHub's native shell."""
import html
import re
import shutil
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root / "visual-preview"
out.mkdir(exist_ok=True)
readme = (root / "README.md").read_text()
# Preserve image/link rows; skip prose/details in this asset-only preview.
rows = []
for block in re.split(r"\n\s*\n", readme):
    if "<img " not in block:
        continue
    tags = re.findall(r'<a\s+href="[^"]+">|</a>|<img\s+[^>]+>|<br\s*/?>', block)
    rendered = []
    for tag in tags:
        if tag.startswith("<img"):
            tag = re.sub(r'src="([^"]+)"', lambda m: 'src="' + (root/m[1]).as_uri() + '"', tag)
            tag = re.sub(r'width="([0-9]+)%"', r'style="width:\1%"', tag)
        rendered.append(tag)
    rows.append("<div class='row'>" + "".join(rendered) + "</div>")
chrome = shutil.which("google-chrome") or shutil.which("chromium")
if not chrome:
    raise RuntimeError("Chrome unavailable on runner")
for theme, width, height in [("dark",900,1900), ("light",900,1900), ("mobile",375,1150)]:
    bg = "#fff" if theme == "light" else "#0d1117"
    page = out / (theme + ".html")
    page.write_text("""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><style>
    *{box-sizing:border-box}body{margin:0;background:"""+bg+""";font-family:Arial}main{width:"""+str(width-24)+"""px;margin:12px auto;max-width:calc(100% - 24px)}.row{font-size:0;line-height:0;text-align:center;margin:0 0 5px}img{height:auto;vertical-align:middle;max-width:100%}a{display:contents}</style></head><body><main>"""+ "".join(rows)+"""</main><script>
    window.addEventListener('load',()=>{const imgs=[...document.images]; const ok=imgs.length>=15&&imgs.every(i=>i.complete&&i.naturalWidth>0&&i.getBoundingClientRect().right<=document.documentElement.clientWidth+1);document.body.setAttribute('data-qa',ok?'PASS':'FAIL');});
    </script></body></html>""",encoding="utf-8")
    cmd = [chrome,"--headless","--no-sandbox","--disable-gpu","--hide-scrollbars","--allow-file-access-from-files",f"--window-size={max(500,width)},{height}","--virtual-time-budget=2000"]
    # Chrome desktop headless has a minimum viewport width; the main content is
    # explicitly constrained to 351px for the mobile simulation.
    dom = subprocess.run(cmd+["--dump-dom",page.as_uri()],capture_output=True,text=True,check=True,timeout=45).stdout
    assert 'data-qa="PASS"' in dom, theme
    screenshot=out/(theme+".png")
    subprocess.run(cmd+[f"--screenshot={screenshot}",page.as_uri()],capture_output=True,check=True,timeout=45)
    assert screenshot.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    print(f"Visual smoke: {theme}, content width {width-24}px, all image assets loaded; screenshot created.")
