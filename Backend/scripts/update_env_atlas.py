import os
import re

brain_dir = r"C:\Users\Digisha\.gemini\antigravity-ide\brain"
atlas_uri = None

for root, dirs, files in os.walk(brain_dir):
    for f in files:
        if f.endswith(".jsonl"):
            p = os.path.join(root, f)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                    for line in fp:
                        if "mongodb+srv://" in line:
                            # Match mongodb+srv://... up to quote/space/backslash
                            m = re.search(r"mongodb\+srv://[a-zA-Z0-9\:\@\.\_\-\?\=\&\%\+\/]+", line)
                            if m:
                                atlas_uri = m.group(0)
                                print("Found Atlas URI in:", p)
                                break
                        if atlas_uri:
                            break
            except Exception:
                pass
        if atlas_uri:
            break

if atlas_uri:
    print("Clean match length:", len(atlas_uri))
    print("Is valid alphanumeric/url chars:", bool(re.match(r"^mongodb\+srv://[a-zA-Z0-9\:\@\.\_\-\?\=\&\%\+\/]+$", atlas_uri)))
    
    with open(".env", "r", encoding="utf-8") as f:
        env_lines = f.readlines()

    new_lines = []
    has_mongo_url = False
    has_mongo_uri = False
    for l in env_lines:
        if l.startswith("MONGODB_URL="):
            new_lines.append(f"MONGODB_URL={atlas_uri}\n")
            has_mongo_url = True
        elif l.startswith("MONGODB_URI="):
            new_lines.append(f"MONGODB_URI={atlas_uri}\n")
            has_mongo_uri = True
        elif l.startswith("MONGODB_DATABASE="):
            new_lines.append("MONGODB_DATABASE=placementor\n")
        else:
            new_lines.append(l)

    if not has_mongo_url and not has_mongo_uri:
        new_lines.insert(0, f"MONGODB_URL={atlas_uri}\n")

    with open(".env", "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("Successfully updated Backend/.env with clean Atlas URI!")
else:
    print("Atlas URI not found in brain transcripts.")
