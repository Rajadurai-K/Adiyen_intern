import re
import json

# Book name
BOOK_NAME = "Visistadvaita-1977"

# Read OCR text
with open(r"C:\Users\rajad\OneDrive\Desktop\Adiyen_intern\Task 2\book 1\Visistadvaita-1977.txt", "r", encoding="utf-8") as file:
    text = file.read()
    

# Regex pattern to match chapters and appendices
pattern = re.compile(
    r'(CHAPTER\s+[IVX]+|APPENDIX\s+[A-Z])\s*\n\s*([^\n]+)\s*\n(.*?)(?=\n\s*CHAPTER\s+[IVX]+|\n\s*APPENDIX\s+[A-Z]|\Z)',
    re.DOTALL | re.IGNORECASE
)

matches = pattern.findall(text)
print(f"✅ Found {len(matches)} chapters/appendices")

# Build structured JSON chunks
structured_chunks = []
for chapter_type, chapter_title, chapter_content in matches:
    # Build ref dynamically
    ref = f"{BOOK_NAME} -> {chapter_type.strip()}, {chapter_title.strip()}"

    # Clean up chapter content
    chunk = re.sub(r'\s+', ' ', chapter_content).strip()

    structured_chunks.append({
        "chunk": chunk,
        "ref": ref
    })

# Save JSON
with open('chapter_final.json', 'w', encoding='utf-8') as json_file:
    json.dump(structured_chunks, json_file, ensure_ascii=False, indent=2)

print(f"✅ Successfully created {len(structured_chunks)} structured chunks in structured_book_chunks.json")
