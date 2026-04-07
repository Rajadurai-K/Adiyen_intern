import re
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "7463.txt"
OUTPUT_FILE = "7463_output.json"

# Translation table for numbers
dev_to_num = str.maketrans("०१२३४५६७८९", "0123456789")

def parse_suta_samhita():
    lines = Path(INPUT_FILE).read_text(encoding="utf-8").splitlines()
    
    results = []
    book_name = "शाङ्खायनश्रौतसूत्रम् (द्वितीयो भागः)"
    chapter_no = ""
    
    # Buffer for commentary
    line_queue = []
    
    # Pattern: १. २. ३.
    verse_pattern = re.compile(r"^([०-९0-9]+)\.")

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue

        # Chapter detection
        if clean_line.lower().startswith("chapter"):
            parts = clean_line.split()
            if len(parts) > 1:
                chapter_no = parts[1].translate(dev_to_num)
            continue

        match = verse_pattern.match(clean_line)

        if match:
            # Save previous commentary
            if results and line_queue:
                results[-1]["commentary"] = " ".join(line_queue).strip()

            v_num_dev = match.group(1)
            v_num = v_num_dev.translate(dev_to_num)

            results.append({
                "devverse": clean_line,
                "ref": f"{book_name} ->{chapter_no}.{v_num}"
            })

            line_queue = []
        else:
            line_queue.append(clean_line)

    # Save last commentary
    if results and line_queue:
        results[-1]["commentary"] = " ".join(line_queue).strip()

    return results


# Run
data = parse_suta_samhita()

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Done! {len(data)} verses processed.")