import re
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "1225.txt"
OUTPUT_FILE = "1225_output.json"

dev_to_num = str.maketrans("०१२३४५६७८९", "0123456789")

def parse_suta_samhita():
    lines = Path(INPUT_FILE).read_text(encoding="utf-8").splitlines()
    
    results = []
    book_name = "ज्योतिर्निबन्धः"
    
    chapter_no = ""
    chapter_name = ""
    waiting_for_chapter_name = False
    
    line_queue = []
    
    verse_end_pattern = re.compile(r"॥\s*([०-९0-9]+)\s*॥$")

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue

        # 🔹 Step 1: detect chapter number
        if clean_line.lower().startswith("chapter"):
            parts = clean_line.split()
            if len(parts) > 1:
                chapter_no = parts[1].translate(dev_to_num)

            chapter_name = ""
            waiting_for_chapter_name = True
            continue

        # 🔹 Step 2: assign chapter name (IMPROVED LOGIC 🔥)
        if waiting_for_chapter_name:
            if (
                "अध्यायः" in clean_line
                or clean_line.startswith("अथ")
                or (clean_line.endswith("।") and len(clean_line) < 60)
            ):
                chapter_name = clean_line.replace("॥", "").strip()
                waiting_for_chapter_name = False
                continue

        # 🔹 Add line to buffer
        line_queue.append(clean_line)

        match = verse_end_pattern.search(clean_line)

        if match:
            v_num_dev = match.group(1)
            v_num = v_num_dev.translate(dev_to_num)

            devverse_text = "\n".join(line_queue)

            # 🔥 fallback if still empty
            current_chapter = chapter_name if chapter_name else "प्रस्तावना"

            results.append({
                "verse": devverse_text,
                "ref": f"{book_name} -> {current_chapter} -> {v_num}"
            })

            line_queue = []

    return results


# Run parser
data = parse_suta_samhita()

# Save JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Done! {len(data)} verses processed.")