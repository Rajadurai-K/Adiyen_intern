import re
import json
from pathlib import Path

# Setup file paths
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "7221.txt" 
OUTPUT_FILE = BASE_DIR / "7221_output.json"

# Translation table for Devanagari numbers to Arabic
dev_to_num = str.maketrans("०१२३४५६७८९", "0123456789")

def parse_tattva_dipika_final():
    if not Path(INPUT_FILE).exists():
        print(f"Error: {INPUT_FILE} not found.")
        return []

    # Read the whole file and split into blocks by blank lines
    content = INPUT_FILE.read_text(encoding="utf-8")
    blocks = re.split(r'\n\s*\n', content)
    
    results = []
    current_book = "Unknown"
    current_chapter = ""
    current_section = ""
    
    # Regex patterns
    re_book = re.compile(r'^\s*book\s*[:：]\s*(.*)', re.I)
    re_chapter = re.compile(r'^\s*chapter\s*[:：]\s*(.*)', re.I)
    re_section = re.compile(r'^\s*section\s*[:：]\s*(.*)', re.I)
    # Finds verse numbers like ॥ १ ॥ or 1. at the end of a block
    re_verse_marker = re.compile(r'([०-९0-9]+)\s*[।॥\s]*$')

    for block in blocks:
        clean_block = block.strip()
        if not clean_block:
            continue

        # 1. Handle Headers (Book, Chapter, Section)
        book_match = re_book.match(clean_block)
        if book_match:
            current_book = book_match.group(1).strip() or "Book"
            continue

        chap_match = re_chapter.match(clean_block)
        if chap_match:
            val = chap_match.group(1).strip()
            current_chapter = f"Chapter {val}" if val else "Chapter"
            current_section = "" 
            continue

        sect_match = re_section.match(clean_block)
        if sect_match:
            val = sect_match.group(1).strip()
            current_section = f"Section {val}" if val else "Section"
            continue

        # 2. Check if this block is a Verse (contains a number at the end)
        num_match = re_verse_marker.search(clean_block)
        if num_match:
            v_num_dev = num_match.group(1)
            v_num_arabic = v_num_dev.translate(dev_to_num)
            
            # The ENTIRE block is the verse. We just strip the number from the end.
            verse_text = clean_block[:num_match.start()].strip()
            verse_text = re.sub(r'[\s\-।॥]+$', '', verse_text)
            
            ref_str = f"{current_book} -> {current_chapter} -> {current_section} -> {v_num_arabic}"
            
            results.append({
                "verse": verse_text,
                "commentary": "",
                "ref": ref_str
            })
        
        # 3. If no number is found, it is Commentary for the previous verse
        else:
            if results:
                # Append the current block to the commentary of the last added verse
                if results[-1]["commentary"]:
                    results[-1]["commentary"] += "\n\n" + clean_block
                else:
                    results[-1]["commentary"] = clean_block

    return results

# Run and save
data = parse_tattva_dipika_final()
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Process Complete! Total items: {len(data)}")