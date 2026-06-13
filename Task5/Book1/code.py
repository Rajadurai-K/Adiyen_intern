import re
import json
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent 
INPUT_FILE = BASE_DIR / "तत्त्वदीपिका (ब्रह्मसूत्रभाष्यटीका).txt"
OUTPUT_FILE = BASE_DIR / "tattva_dipika_output.json"

dev_to_num = str.maketrans("०१२३४५६७८९", "0123456789")

def parse_tattva_dipika():
    if not Path(INPUT_FILE).exists():
        print(f"Error: {INPUT_FILE} not found.")
        return []
        
    # We use splitlines without stripping immediately so we can detect blank lines
    lines = Path(INPUT_FILE).read_text(encoding="utf-8").splitlines()
    
    results = []
    book_name = "तत्त्वदीपिका"
    
    current_chapter = ""
    current_pada = ""
    current_subdivision = ""
    verse_counter = 0
    
    line_queue = []

    re_chapter = re.compile(r"^(First|Second|Third|Fourth)\s+Chapter:?\s*(.*)", re.I)
    re_pada = re.compile(r"^(First|Second|Third|Fourth)\s+Pada", re.I)
    re_subdiv_marker = re.compile(r"^sub division\s*:\s*(.*)", re.I)
    re_verse_end_num = re.compile(r"।।\s*([०-९0-9]+)\s*।।$")

    def save_current_verse():
        nonlocal line_queue, verse_counter
        if not line_queue:
            return
            
        verse_text = "\n".join(line_queue).strip()
        if not verse_text:
            line_queue = []
            return

        # Increment counter
        verse_counter += 1
        
        # Check if the last line had an explicit number like ।। ५६ ।।
        # if it did, we use that number instead for the reference
        last_line = line_queue[-1].strip()
        num_match = re_verse_end_num.search(last_line)
        if num_match:
            verse_counter = int(num_match.group(1).translate(dev_to_num))

        # Build Hierarchy Reference
        ref_parts = [book_name, current_chapter]
        if current_pada:
            ref_parts.append(current_pada)
        if current_subdivision:
            ref_parts.append(current_subdivision)
        ref_parts.append(str(verse_counter))
        
        results.append({
            "verse": verse_text,
            "ref": " -> ".join(ref_parts)
        })
        line_queue = []

    for line in lines:
        clean_line = line.strip()

        # Handle Blank Lines (Verse Separators)
        if not clean_line:
            save_current_verse()
            continue

        # Detect Chapter
        chap_match = re_chapter.match(clean_line)
        if chap_match:
            save_current_verse()
            current_chapter = chap_match.group(1) + " Chapter"
            current_pada = ""
            current_subdivision = ""
            verse_counter = 0
            continue
        
        if "अध्यायः" in clean_line and len(clean_line) < 35:
            save_current_verse()
            current_chapter = clean_line
            current_pada = ""
            current_subdivision = ""
            verse_counter = 0
            continue

        # Detect Pada
        pada_match = re_pada.match(clean_line)
        if pada_match:
            save_current_verse()
            current_pada = clean_line.split("।।")[0].strip()
            current_subdivision = ""
            verse_counter = 0
            continue

        # Detect Subdivision
        subdiv_match = re_subdiv_marker.match(clean_line)
        if subdiv_match:
            save_current_verse()
            current_subdivision = subdiv_match.group(1).strip()
            verse_counter = 0 
            continue

        # If it's a normal line, add it to the current verse queue
        line_queue.append(clean_line)
        
        # Hard break if line ends with double danda and a number 
        # (Handles cases where there might not be a blank line after a numbered verse)
        if re_verse_end_num.search(clean_line):
            save_current_verse()

    # Final save for the last block
    save_current_verse()

    return results

# Run
data = parse_tattva_dipika()

# Save JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Successfully processed {len(data)} sections.")