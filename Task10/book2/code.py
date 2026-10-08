import re
import json
from pathlib import Path

# Setup file paths
BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "8490.txt"
OUTPUT_FILE = BASE_DIR / "8490_output.json"

def parse_commentary_to_chunks():
    if not Path(INPUT_FILE).exists():
        print(f"Error: {INPUT_FILE} not found.")
        return []

    # Read content and split into paragraphs by double newlines
    content = Path(INPUT_FILE).read_text(encoding="utf-8")
    blocks = re.split(r'\n\s*\n', content)
    
    results = []
    current_book = "Unknown Book"
    current_chapter = "General"
    commentary_count = 0
    
    # Regex patterns for headers
    book_pattern = re.compile(r'^book\s*[:：]\s*(.*)', re.I)
    chapter_pattern = re.compile(r'^chapter\s*[:：]\s*(.*)', re.I)

    for block in blocks:
        clean_block = block.strip()
        if not clean_block:
            continue

        # 1. Detect Book Name Header
        book_match = book_pattern.match(clean_block)
        if book_match:
            current_book = book_match.group(1).strip()
            continue

        # 2. Detect Chapter Header
        chapter_match = chapter_pattern.match(clean_block)
        if chapter_match:
            current_chapter = chapter_match.group(1).strip()
            commentary_count = 0  # Reset counter for every new chapter
            continue

        # 3. Process Paragraphs as Commentary Chunks
        commentary_count += 1
        
        # Build Reference: book name -> chapter -> commentary number
        ref_str = f"{current_book} -> {current_chapter} -> {commentary_count}"
        
        results.append({
            "commentary": clean_block,
            "ref": ref_str
        })

    return results

# Run and save
data = parse_commentary_to_chunks()

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Done! Processed {len(data)} commentary chunks.")