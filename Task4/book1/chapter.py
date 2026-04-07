import re
import json

from pathlib import Path

BASE_DIR = Path(__file__).parent
file_path = BASE_DIR / "BHAGAVAT-GITA.txt"

with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()

# Regex: Capture CHAPTER + Roman number + Title + Content
pattern = re.compile(
    r'CHAPTER\s+([IVX]+)\s*\n\s*([^\n]+)\n(.*?)(?=\n\s*CHAPTER\s+[IVX]+|\Z)',
    re.DOTALL | re.IGNORECASE
)

matches = pattern.findall(text)

print(f"✅ Found {len(matches)} chapters")

structured_chunks = []

for chapter_num, chapter_title, chapter_content in matches:
    
    # Clean content
    chunk = re.sub(r'\s+', ' ', chapter_content).strip()

    # Build ref in your format
    ref = f"{'THE BHAGAVAD GITA'} -> Chapter {chapter_num} -> {chapter_title.strip()} -> Introduction"

    structured_chunks.append({
        "chunk": chunk,
        "ref": ref
    })

# Save JSON
with open("chapter_final.json", "w", encoding="utf-8") as f:
    json.dump(structured_chunks, f, ensure_ascii=False, indent=2)

print("✅ chapter_final.json created successfully")