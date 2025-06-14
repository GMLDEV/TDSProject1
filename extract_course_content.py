import os
import markdown
from bs4 import BeautifulSoup
import json

input_dir = "C:/Users/Gagan/tools-in-data-science-public"
output_file = "course_content.json"

def md_to_text(md_content):
    html = markdown.markdown(md_content)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

documents = []

for root, _, files in os.walk(input_dir):
    for file in files:
        if file.endswith(".md") or file.endswith(".html"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
                if not raw.strip():
                    continue

                if file.endswith(".md"):
                    text = md_to_text(raw)
                else:
                    soup = BeautifulSoup(raw, "html.parser")
                    text = soup.get_text()

                documents.append({
                    "file": file,
                    "path": path,
                    "content": text.strip()
                })

# Write everything to a single JSON file
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(documents, f, indent=2, ensure_ascii=False)

print(f"✅ Extracted {len(documents)} documents into {output_file}")
