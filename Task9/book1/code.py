import re
import json
from pathlib import Path

# Setup file paths
BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "7099.txt"
OUTPUT_FILE = BASE_DIR / "7099_output.json"

# Translation table for numbers (Devanagari to Arabic)
dev_to_num = str.maketrans("०१२३४५६७८९", "0123456789")

def is_pure_devanagari(text):
    """Returns True if the text has Devanagari and NO English letters."""
    has_devanagari = bool(re.search(r'[\u0900-\u097F]', text))
    has_english = bool(re.search(r'[a-zA-Z]', text))
    return has_devanagari and not has_english

def parse_bhakti_sutras():
    if not Path(INPUT_FILE).exists():
        print(f"Error: {INPUT_FILE} not found.")
        return []

    # Read content and split into paragraphs/blocks
    content = Path(INPUT_FILE).read_text(encoding="utf-8")
    blocks = re.split(r'\n\s*\n', content)
    
    results = []
    book_name = "भक्तिसूत्रम्" # Default
    
    # Regex to extract numbers from ॥१॥ or ॥1॥
    num_extractor = re.compile(r'॥([०-९0-9]+)॥')
    # Regex to find 'book : name'
    book_pattern = re.compile(r'book\s*:\s*(.*)', re.I)

    for block in blocks:
        clean_block = block.strip()
        if not clean_block:
            continue

        # 1. Check for Book Name header
        book_match = book_pattern.match(clean_block)
        if book_match:
            book_name = book_match.group(1).strip()
            continue

        # 2. Check if block is a pure Sanskrit Verse
        if is_pure_devanagari(clean_block):
            # Extract verse number for the reference
            v_num = "0"
            match_num = num_extractor.search(clean_block)
            if match_num:
                v_num = match_num.group(1).translate(dev_to_num)
            
            results.append({
                "verse": clean_block,
                "commentary": "",
                "ref": f"{book_name} -> {v_num}"
            })
        
        # 3. If block contains English, it is commentary for the current verse
        else:
            if results:
                # If commentary already exists, append with double newline
                if results[-1]["commentary"]:
                    results[-1]["commentary"] += "\n\n" + clean_block
                else:
                    results[-1]["commentary"] = clean_block

    return results

# Run and save
data = parse_bhakti_sutras()

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Done! {len(data)} verses processed. Saved to {OUTPUT_FILE}")