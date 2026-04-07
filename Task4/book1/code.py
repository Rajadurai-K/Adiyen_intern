import re
import json
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "surya_ocr_Bhagavad-Gita.with.the.Commentary.of.Sri.Shankaracharya.txt"
OUTPUT_FILE = "gita_verse_output.json"

# Devanagari to English number translation
dev_to_num = str.maketrans("०१२३४५६७८९", "0123456789")

def parse_gita():
    if not INPUT_FILE.exists():
        print(f"Error: {INPUT_FILE} not found.")
        return

    content = INPUT_FILE.read_text(encoding="utf-8")
    lines = content.splitlines()

    results = []
    book_name = "THE BHAGAVAD GITA"
    chapter_name = "INTRO"
    
    # regex to find verse endings: ॥ 1 ॥ or ॥ १ ॥
    verse_pattern = re.compile(r"॥\s*([०-९0-9]+)\s*॥")
    
    # Temporary storage
    buffer = []

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue

        # 1. Detect Chapter / Discourse Headers
        if "DISCOURSE" in clean_line.upper() or "CHAPTER" in clean_line.upper():
            chapter_name = clean_line
            continue

        buffer.append(clean_line)
        
        # 2. Detect Verse Number
        match = verse_pattern.search(clean_line)
        if match:
            verse_num = match.group(1).translate(dev_to_num)
            
            # Logic: The last 1 or 2 Sanskrit lines in the buffer are the verse.
            # Everything in the buffer BEFORE those Sanskrit lines belongs 
            # to the commentary of the PREVIOUS verse.
            
            # Identify which lines are part of the current shloka
            # We look for the last few lines that contain Devanagari
            shloka_lines = []
            prose_lines = []
            
            # Iterate backwards to grab the shloka
            found_shloka = False
            for b_line in reversed(buffer):
                if re.search(r"[\u0900-\u097F]", b_line): # If contains Sanskrit
                    shloka_lines.insert(0, b_line)
                    found_shloka = True
                elif not found_shloka:
                    # Haven't hit the shloka yet (rare for this file structure)
                    continue
                else:
                    # We have finished grabbing the shloka, rest is previous commentary
                    prose_lines.insert(0, b_line)
            
            # 3. Attach prose to the PREVIOUS verse in results
            if results and prose_lines:
                # Clean up junk like "THE BHAGAVAD-GITA" or page numbers
                cleaned_commentary = " ".join(prose_lines)
                cleaned_commentary = re.sub(r"THE BHAGAVAD-GITA|DIS\..*", "", cleaned_commentary).strip()
                results[-1]["commentary"] = cleaned_commentary

            # 4. Add the NEW verse to the results list
            results.append({
                "devverse": "\n".join(shloka_lines).strip(),
                "commentary": "", # Placeholder to be filled by the next verse's look-back
                "ref": f"{book_name} -> {chapter_name} -> {verse_num}"
            })

            # Clear buffer for next cycle
            buffer = []

    # Final Cleanup for the very last verse in the file
    if results and buffer:
        results[-1]["commentary"] = " ".join(buffer).strip()

    return results

# Execute and Save
data = parse_gita()
if data:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Successfully extracted {len(data)} verses to {OUTPUT_FILE}")