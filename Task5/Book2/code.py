import re
import json
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent 
INPUT_FILE = BASE_DIR / "ब्रह्मसूत्राणुभाष्यम्.txt"
OUTPUT_FILE = BASE_DIR / "ब्रह्मसूत्राणुभाष्यम्_output.json"

dev_to_num = str.maketrans("०१२३४५६७८९", "0123456789")

def parse_tattva_dipika():
    if not Path(INPUT_FILE).exists():
        print(f"Error: {INPUT_FILE} not found.")
        return []
        
    lines = Path(INPUT_FILE).read_text(encoding="utf-8").splitlines()
    
    results = []
    book_name = "ब्रह्मसूत्राणुभाष्यम्"
    
    current_chapter = ""
    current_pada = ""
    current_subdivision = ""
    verse_counter = 0
    
    line_queue = []

    # Regex Patterns - Improved to handle text after colon or standard headers
    re_chapter = re.compile(r".*Chapter\s*:\s*(.*)", re.I)
    re_pada = re.compile(r".*Pada\s*:\s*(.*)", re.I)
    re_subdiv = re.compile(r".*sub division\s*:\s*(.*)", re.I)
    re_verse_end_num = re.compile(r"।।\s*([०-९0-9]+)\s*।।$")

    def save_current_verse():
        nonlocal line_queue, verse_counter
        if not line_queue:
            return
            
        verse_text = "\n".join(line_queue).strip()
        if not verse_text:
            line_queue = []
            return

        verse_counter += 1
        
        # Sync counter if explicit number exists (e.g., ।। ५ ।।)
        last_line = line_queue[-1].strip()
        num_match = re_verse_end_num.search(last_line)
        if num_match:
            verse_counter = int(num_match.group(1).translate(dev_to_num))

        # Build Hierarchy Reference
        ref_parts = [book_name]
        
        if current_chapter:
            ref_parts.append(current_chapter)
        
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

        # 1. Detect Chapter
        chap_match = re_chapter.match(clean_line)
        if chap_match:
            save_current_verse()
            name = chap_match.group(1).strip()
            current_chapter = name if name else "Chapter"
            current_pada = ""
            current_subdivision = ""
            verse_counter = 0
            continue
            
        if "अध्यायः" in clean_line and ":" not in clean_line and len(clean_line) < 35:
            save_current_verse()
            current_chapter = clean_line
            current_pada = ""
            current_subdivision = ""
            verse_counter = 0
            continue

        # 2. Detect Pada
        pada_match = re_pada.match(clean_line)
        if pada_match:
            save_current_verse()
            name = pada_match.group(1).strip()
            # Capture name after colon, or the part before danda if no colon
            current_pada = name if name else clean_line.split("।।")[0].strip()
            current_subdivision = "" 
            verse_counter = 0
            continue

        # 3. Detect Subdivision
        subdiv_match = subdiv_match = re_subdiv.match(clean_line)
        if subdiv_match:
            save_current_verse()
            current_subdivision = subdiv_match.group(1).strip()
            verse_counter = 0 
            continue

        # Add line to queue
        line_queue.append(clean_line)
        
        # Immediate save for explicitly numbered verses
        if re_verse_end_num.search(clean_line):
            save_current_verse()

    # Final save
    save_current_verse()

    return results

# Execution
data = parse_tattva_dipika()
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Successfully processed {len(data)} sections.")