import re
import json
from pathlib import Path

# Setup file paths
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "7255.txt" 
OUTPUT_FILE = BASE_DIR / "7255_output.json"

def is_root_verse(text):
    """
    Stricter check: A block is a root verse only if it contains 
    Devanagari characters AND contains NO English letters.
    Commentaries always contain English (translations/explanations).
    """
    devanagari_chars = re.findall(r'[\u0900-\u097F]', text)
    english_chars = re.findall(r'[a-zA-Z]', text)
    
    # Must have Devanagari and MUST NOT have English letters
    if devanagari_chars and not english_chars:
        return True
    return False

def parse_vedic_text_v6():
    if not Path(INPUT_FILE).exists():
        print(f"Error: {INPUT_FILE} not found.")
        return []

    # Read file and split by double newlines
    content = INPUT_FILE.read_text(encoding="utf-8")
    blocks = re.split(r'\n\s*\n', content)
    
    results = []
    current_book = "Unknown Book"
    current_chapter = "Unknown Chapter"
    current_lesson = "0"
    verse_counter = 0
    
    # Regex for headers
    re_book = re.compile(r'^\s*book\s*[:：]\s*(.*)', re.I)
    re_chapter = re.compile(r'^\s*chapter\s*[:：]\s*(.*)', re.I)
    re_lesson = re.compile(r'^\s*lesson\s*[:：]\s*(.*)', re.I)

    for block in blocks:
        clean_block = block.strip()
        if not clean_block:
            continue

        # 1. Handle Hierarchy Headers
        book_match = re_book.match(clean_block)
        if book_match:
            current_book = book_match.group(1).strip()
            continue

        chapter_match = re_chapter.match(clean_block)
        if chapter_match:
            current_chapter = chapter_match.group(1).strip()
            continue

        lesson_match = re_lesson.match(clean_block)
        if lesson_match:
            current_lesson = lesson_match.group(1).strip()
            verse_counter = 0  # Reset verse count for each new lesson
            continue

        # 2. Identify Verse vs Commentary
        if is_root_verse(clean_block):
            verse_counter += 1
            
            # UPDATED: Added "Lesson" explicitly into the reference string
            ref_str = f"{current_book} -> {current_chapter} -> Lesson {current_lesson} -> {verse_counter}"
            
            results.append({
                "verse": clean_block,
                "commentary": "",
                "ref": ref_str
            })
        else:
            # If it has English or is a mix, it is commentary for the preceding verse
            if results:
                if results[-1]["commentary"]:
                    results[-1]["commentary"] += "\n\n" + clean_block
                else:
                    results[-1]["commentary"] = clean_block

    return results

# Process and Save
data = parse_vedic_text_v6()

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Process Complete! Total items: {len(data)}")