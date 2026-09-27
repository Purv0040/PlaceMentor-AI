import os
import re

logs_dir = r"C:\Users\Digisha\.gemini\antigravity-ide\brain"
matches = set()

for root, dirs, files in os.walk(logs_dir):
    for f in files:
        if f.endswith(".jsonl"):
            p = os.path.join(root, f)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                    for line in fp:
                        if "mongodb+srv://" in line:
                            for m in re.finditer(r"mongodb\+srv://[^\s\"'\`\,\{\}\<\>\\]+", line):
                                uri = m.group(0)
                                matches.add(uri)
            except Exception:
                pass

print(f"Total mongodb+srv URIs found across all transcripts: {len(matches)}")
for uri in matches:
    print(f"URI: {uri}")
