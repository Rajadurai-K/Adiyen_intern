import re
import json
from pathlib import Path

# Setup file paths
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "7252.txt" 
OUTPUT_FILE = BASE_DIR / "7252_output.json"

def is_devanagari_block(text):
    """
    Checks if a block is primarily Devanagari (Sanskrit/Hindi).
    Matches characters in the Devanagari Unicode range.
    """
    devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))
    total_alpha = len(re.findall(r'[a-zA-Z\u0900-\u097F]', text))
    
    if total_alpha == 0:
        return False
    
    # If more than 20% of text is Devanagari, we treat it as a Verse block
    return (devanagari_chars / total_alpha) > 0.2

def parse_vedic_text_v3():
    if not Path(INPUT_FILE).exists():
        print(f"Error: {INPUT_FILE} not found.")
        return []

    # Read the file and split into paragraphs by double newlines
    content = INPUT_FILE.read_text(encoding="utf-8")
    blocks = re.split(r'\n\s*\n', content)
    
    results = []
    current_book = "Unknown Book"
    current_anuvaka = "0"
    verse_counter = 0
    
    # Regex for headers
    re_book = re.compile(r'^\s*book\s*[:：]\s*(.*)', re.I)
    re_anuvaka = re.compile(r'^\s*anuvaka\s*[:：]\s*(.*)', re.I)

    for block in blocks:
        clean_block = block.strip()
        if not clean_block:
            continue

        # 1. Handle Headers
        book_match = re_book.match(clean_block)
        if book_match:
            current_book = book_match.group(1).strip()
            continue

        anuvaka_match = re_anuvaka.match(clean_block)
        if anuvaka_match:
            current_anuvaka = anuvaka_match.group(1).strip()
            verse_counter = 0 # Reset verse count for each new Anuvaka
            continue

        # 2. Identify Verse vs Commentary
        if is_devanagari_block(clean_block):
            # It's a new Verse block
            verse_counter += 1
            ref_str = f"{current_book} -> {current_anuvaka} -> {verse_counter}"
            
            results.append({
                "verse": clean_block,
                "commentary": "",
                "ref": ref_str
            })
        else:
            # It's an English block (Commentary)
            if results:
                # Append to the LAST added verse
                if results[-1]["commentary"]:
                    results[-1]["commentary"] += "\n\n" + clean_block
                else:
                    results[-1]["commentary"] = clean_block
            else:
                # Text appearing before the first verse (skip or handle)
                pass

    return results

# Process and Save
data = parse_vedic_text_v3()

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Process Complete! Total items: {len(data)}")