import re
import json
from pathlib import Path

# Setup file paths
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "7218.txt"
OUTPUT_FILE = BASE_DIR / "7218_output.json"

# Translation table for Devanagari numbers to Arabic
dev_to_num = str.maketrans("०१२३४५६७८९", "0123456789")

def parse_with_commentary():
    if not Path(INPUT_FILE).exists():
        print(f"Error: {INPUT_FILE} not found.")
        return []

    content = INPUT_FILE.read_text(encoding="utf-8")
    
    # Split text into blocks based on blank lines
    blocks = re.split(r'\n\s*\n', content)
    
    results = []
    current_book = "Unknown Book"
    current_part = ""
    current_canto = ""
    
    # Regex for hierarchy labels
    book_pattern = re.compile(r'^\s*book\s*[:：]\s*(.*)$', re.IGNORECASE)
    part_pattern = re.compile(r'^\s*(PART\s+[IVXLCDM0-9]+.*)$', re.IGNORECASE)
    canto_pattern = re.compile(r'^\s*(Canto\s+[IVXLCDM0-9]+.*)$', re.IGNORECASE)
    
    # Regex for verse numbers (e.g., ।।१।। or 1.) at the end of a block
    verse_num_pattern = re.compile(r'([०-९0-9]+)\s*[।॥\s]*$')

    for block in blocks:
        clean_block = block.strip()
        if not clean_block:
            continue

        # 1. Detect Book Name
        book_match = book_pattern.match(clean_block)
        if book_match:
            current_book = book_match.group(1).strip()
            continue

        # 2. Detect Part
        part_match = part_pattern.match(clean_block)
        if part_match:
            current_part = part_match.group(1).strip()
            continue

        # 3. Detect Canto
        canto_match = canto_pattern.match(clean_block)
        if canto_match:
            current_canto = canto_match.group(1).strip()
            continue

        # 4. Detect Verse (block ending in a number)
        num_match = verse_num_pattern.search(clean_block)
        if num_match:
            v_num_dev = num_match.group(1)
            v_num_arabic = v_num_dev.translate(dev_to_num)
            
            # Extract verse text
            verse_text = clean_block[:num_match.start()].strip()
            verse_text = re.sub(r'[\s\-।॥]+$', '', verse_text)
            
            # Create a new entry
            results.append({
                "verse": verse_text,
                "commentary": "",
                "ref": f"{current_book} -> {current_part} -> {current_canto} -> {v_num_arabic}"
            })
        
        # 5. If it's not a label and not a verse, it's commentary for the current verse
        else:
            if results:
                # Append this block to the commentary of the most recent verse
                if results[-1]["commentary"]:
                    results[-1]["commentary"] += "\n\n" + clean_block
                else:
                    results[-1]["commentary"] = clean_block

    return results

# Execute and Save
data = parse_with_commentary()

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Process Complete!")
print(f"Total items processed: {len(data)}")
print(f"Output saved to: {OUTPUT_FILE}")