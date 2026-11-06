import re

ARTIFACT_PATH = r"C:\Users\mhs4118\.gemini\antigravity\brain\38ec0b63-c099-4411-a09e-791a249c2aa3\gorkha_landslides_3d_viewer.html"
WEB_INDEX_PATH = r"C:\Users\mhs4118\.gemini\antigravity\scratch\gorkha-landslides-3d\index.html"

with open(ARTIFACT_PATH, "r", encoding="utf-8") as f:
    art = f.read()

rem = re.findall(r"fp6a", art, re.IGNORECASE)
assert len(rem) == 0, f"Still found fp6a in artifact: {rem}"

# Sync index.html from artifact HTML while preserving standalone CSS variables (:root / html.light)
standalone_vars = (
    "  <style>\n"
    "    :root { --background: #0b0f19; --foreground: #f1f5f9; --card: #111827; --border: #1e293b; --muted-foreground: #94a3b8; --primary: #38bdf8; }\n"
    "    html.light { --background: #f8fafc; --foreground: #0f172a; --card: #ffffff; --border: #e2e8f0; --muted-foreground: #64748b; --primary: #0284c7; }\n"
)

art_norm = art.replace("\r\n", "\n")
assert "  <style>\n" in art_norm
web_norm = art_norm.replace("  <style>\n", standalone_vars, 1)

rem_web = re.findall(r"fp6a", web_norm, re.IGNORECASE)
assert len(rem_web) == 0, f"Still found fp6a in index.html: {rem_web}"

with open(WEB_INDEX_PATH, "w", encoding="utf-8", newline="\n") as f:
    f.write(web_norm)

print("Verified 0 occurrences of 'fp6a' in both gorkha_landslides_3d_viewer.html and index.html")
