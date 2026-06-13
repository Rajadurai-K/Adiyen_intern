import re
import json
from pathlib import Path

# Setup file paths
BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "3943.txt"
OUTPUT_FILE = BASE_DIR / "3943_output.json"

# Translation table for Devanagari numbers to Arabic
dev_to_num = str.maketrans("०१२३४५६७८९", "0123456789")

def parse_with_chapters():
    # Read the file content
    if not INPUT_FILE.exists():
        print(f"Error: {INPUT_FILE} not found.")
        return []

    content = INPUT_FILE.read_text(encoding="utf-8")
    
    # Split the text into blocks based on blank lines
    blocks = re.split(r'\n\s*\n', content)
    
    results = []
    book_name = "श्रीमाण्डवीशिक्षा"
    current_chapter = "" # Stores the name of the last seen chapter
    
    # Pattern to find numbers at the end of a block (e.g., १ or 1)
    verse_num_pattern = re.compile(r'([०-९0-9]+)\s*$')

    for block in blocks:
        clean_block = block.strip()
        if not clean_block:
            continue

        # Try to find a verse number at the end of the block
        match = verse_num_pattern.search(clean_block)

        # LOGIC TO IDENTIFY CHAPTER HEADINGS:
        # 1. If the block does NOT end in a number, it's likely a heading/chapter.
        # 2. Or if it contains keywords like 'अध्याय' (Chapter) or 'निर्णय' (Decision/Section).
        is_heading = False
        if not match:
            is_heading = True
        elif "अध्याय" in clean_block or "निर्णय" in clean_block or "परिशिष्ट" in clean_block:
            # If the block is very short, it's likely a title even if it has a number
            if len(clean_block.split()) < 6: 
                is_heading = True

        if is_heading:
            current_chapter = clean_block
            continue # Skip adding this as a verse, just save it as the current chapter context

        # IF IT IS A VERSE:
        v_num_dev = match.group(1)
        v_num_arabic = v_num_dev.translate(dev_to_num)
        
        # The verse text is everything before the number
        verse_text = clean_block[:match.start()].strip().rstrip(' -')

        # Build reference: Book -> Chapter -> Verse OR Book -> Verse
        if current_chapter:
            ref_str = f"{book_name} -> {current_chapter} -> {v_num_arabic}"
        else:
            ref_str = f"{book_name} -> {v_num_arabic}"

        results.append({
            "verse": verse_text,
            "ref": ref_str
        })

    return results

# Execute the parser
data = parse_with_chapters()

# Save the output to JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Done! {len(data)} items processed from '{INPUT_FILE}'.")