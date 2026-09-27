import os
import re

search_dirs = [
    r"C:\Users\Digisha\.gemini\antigravity-ide",
    r"C:\Users\Digisha\.gemini",
    r"d:\project\AI placement mentor\PlaceMentor-AI"
]

matches = set()
for base_dir in search_dirs:
    if not os.path.exists(base_dir):
        continue
    for root, dirs, files in os.walk(base_dir):
        # Skip node_modules or venv
        if "node_modules" in root or ".venv" in root or ".git" in root:
            continue
        for f in files:
            if f.endswith((".jsonl", ".txt", ".env", ".json", ".log", ".py", ".md")):
                p = os.path.join(root, f)
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                        content = fp.read()
                        for m in re.finditer(r"mongodb\+srv://[^\s\"'\`]+", content):
                            uri = m.group(0)
                            if "xxxxx" not in uri and "youruser" not in uri and "yourpassword" not in uri:
                                matches.add(uri)
                except Exception:
                    pass

print(f"Found non-placeholder matches: {len(matches)}")
for uri in matches:
    parts = uri.split("@")
    if len(parts) > 1:
        print(f"Match host: {parts[1][:40]}")
    else:
        print(f"Match start: {uri[:30]}")
