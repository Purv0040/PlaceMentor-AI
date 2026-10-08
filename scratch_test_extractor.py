import sys
import os
import json

sys.path.insert(0, os.path.abspath("."))

from ai.app.services.dynamic_extractor import parse_resume_dynamically

with open("Backend/scratch/pdf_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

result = parse_resume_dynamically(text)
print(json.dumps(result, indent=2))

