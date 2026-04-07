import re
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "4848.txt"
OUTPUT_FILE = "4848_output.json"

dev_to_num = str.maketrans("०१२३४५६७८९", "0123456789")

def parse_text():
    lines = Path(INPUT_FILE).read_text(encoding="utf-8").splitlines()

    results = []
    book_name = "कालमाधवकारिका"
    chapter_name = "कालमाधवकारिकाः"

    pattern = re.compile(r"॥\s*([०-९0-9]+)\s*॥")

    groups = {}
    order = []

    # -------- GROUP BY NUMBER --------
    for line in lines:
        clean = line.strip()
        if not clean:
            continue

        match = pattern.search(clean)
        if not match:
            continue

        num = match.group(1).translate(dev_to_num)

        if num not in groups:
            groups[num] = []
            order.append(num)

        groups[num].append(clean)

    # -------- SPLIT VERSE & COMMENTARY --------
    for num in order:
        block = groups[num]

        if len(block) == 1:
            devverse = block[0]
            commentary = ""
        else:
            # 🔥 LAST line = commentary anchor
            # Everything before that → verse
            # Everything after mid → commentary

            split_index = len(block) // 2   # simple & works well here

            devverse = "\n".join(block[:split_index])
            commentary = " ".join(block[split_index:])

        results.append({
            "devverse": devverse.strip(),
            "commentary": commentary.strip(),
            "ref": f"{book_name} -> {chapter_name} -> {num}"
        })

    return results


data = parse_text()

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Done! {len(data)} verses processed.")