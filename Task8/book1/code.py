import re
import json
from pathlib import Path

# Setup file paths - Using resolve() to ensure the path is absolute
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "7211.txt"
OUTPUT_FILE = BASE_DIR / "7211_output.json"

# Translation table for Devanagari numbers to Arabic
dev_to_num = str.maketrans("०१२३४५६७८९", "0123456789")

def parse_with_commentary():
    if not INPUT_FILE.exists():
        print(f"Error: {INPUT_FILE} not found.")
        return []

    # Read content with explicit encoding
    content = INPUT_FILE.read_text(encoding="utf-8")
    
    # Split text into blocks based on one or more blank lines
    blocks = re.split(r'\n\s*\n', content)
    
    results = []
    current_book = "Unknown Book"
    current_part = "प्रारम्भः"
    
    # Robust Regex for labels: looks for 'book' or 'part' followed by a colon
    book_label_pattern = re.compile(r'^\s*book\s*[:：]\s*(.*)$', re.IGNORECASE)
    part_label_pattern = re.compile(r'^\s*part\s*[:：]\s*(.*)$', re.IGNORECASE)
    
    # Flexible Regex for verse numbers: 
    # Finds a number that might be followed by dandas (। or ।।) or spaces at the end of a block
    verse_num_pattern = re.compile(r'([०-९0-9]+)\s*[।॥\s]*$')

    for block in blocks:
        clean_block = block.strip()
        if not clean_block:
            continue

        # 1. Detect Book Name
        book_match = book_label_pattern.match(clean_block)
        if book_match:
            current_book = book_match.group(1).strip()
            continue

        # 2. Detect Part Name
        part_match = part_label_pattern.match(clean_block)
        if part_match:
            current_part = part_match.group(1).strip()
            continue

        # 3. Detect Verse (checks if block contains a number near the end)
        num_match = verse_num_pattern.search(clean_block)
        if num_match:
            v_num_dev = num_match.group(1)
            v_num_arabic = v_num_dev.translate(dev_to_num)
            
            # Extract verse text: remove the number and dandas from the end
            verse_text = clean_block[:num_match.start()].strip()
            # Clean up any remaining leading/trailing punctuation like ' -' or '।।'
            verse_text = re.sub(r'[\s\-।॥]+$', '', verse_text)
            
            results.append({
                "verse": verse_text,
                "commentary": "",
                "ref": f"{current_book} -> {current_part} -> {v_num_arabic}"
            })
        
        # 4. If it's not a label and doesn't end in a number, it's commentary for the last verse
        else:
            if results:
                # Combine multiple commentary blocks if they exist
                if results[-1]["commentary"]:
                    results[-1]["commentary"] += "\n\n" + clean_block
                else:
                    results[-1]["commentary"] = clean_block

    return results

# Run the script
data = parse_with_commentary()

# Save to JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Process Complete!")
print(f"Total items processed: {len(data)}")
print(f"Output saved to: {OUTPUT_FILE}")