import re
import json
from pathlib import Path

# Setup file paths
BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "3572.txt"
OUTPUT_FILE = BASE_DIR / "3572_output.json"

# Translation table for Devanagari numbers to Arabic
dev_to_num = str.maketrans("०१२३४५६७८९", "0123456789")

def parse_pinda_lakshanam():
    # Read the file content
    if not INPUT_FILE.exists():
        print(f"Error: {INPUT_FILE} not found.")
        return []

    content = INPUT_FILE.read_text(encoding="utf-8")
    
    # Split the text into blocks based on blank lines (one or more \n)
    blocks = re.split(r'\n\s*\n', content)
    
    results = []
    book_name = "पिण्डलक्षणम्"
    
    # Pattern to find numbers at the end of a block (e.g., १ or 1)
    verse_num_pattern = re.compile(r'([०-९0-9]+)\s*$')

    for block in blocks:
        clean_block = block.strip()
        if not clean_block:
            continue

        # Look for the verse number at the end of the block
        match = verse_num_pattern.search(clean_block)

        if match:
            v_num_dev = match.group(1)
            v_num_arabic = v_num_dev.translate(dev_to_num)
            
            # The verse text is everything before the number
            verse_text = clean_block[:match.start()].strip()
            
            # Clean up trailing dashes or spaces
            verse_text = verse_text.rstrip(' -')

            # Only append verse and ref
            results.append({
                "verse": verse_text,
                "ref": f"{book_name} -> {v_num_arabic}"
            })
        else:
            # Handle blocks without numbers
            results.append({
                "verse": clean_block,
                "ref": f"{book_name} -> Unknown"
            })

    return results

# Execute the parser
data = parse_pinda_lakshanam()

# Save the output to JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Done! {len(data)} verses processed from '{INPUT_FILE}'.")