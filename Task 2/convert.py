import re
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Constants
BOOK_NAME = "Visistadvaita"
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 400

# Load OCR text of chapters+appendices
with open(r"C:\Users\rajad\OneDrive\Desktop\Adiyen_intern\Task 2\book 1\Visistadvaita-1977.txt", "r", encoding="utf-8") as file:
    text = file.read()
text = re.sub(r'\n\s*\n+', '\n', text) 
# Regex to match chapters and appendices
pattern = re.compile(
    r'(CHAPTER\s+[IVX]+|APPENDIX\s+[A-Z])\s*\n\s*([^\n]+)\s*\n(.*?)(?=\n\s*CHAPTER\s+[IVX]+|\n\s*APPENDIX\s+[A-Z]|\Z)',
    re.DOTALL | re.IGNORECASE
)

matches = pattern.findall(text)
print(f"✅ Found {len(matches)} chapters/appendices")

# Function to split text into overlapping chunks with proper sentence boundaries
# def split_text_with_full_stop(text, chunk_size, overlap):
#     chunks = []
#     start = 0
#     text_length = len(text)

#     while start < text_length:
#         end = min(start + chunk_size, text_length)
#         temp_chunk = text[start:end]

#         # Find the last full stop in temp_chunk
#         last_full_stop = temp_chunk.rfind('.')

#         if last_full_stop != -1:
#             # Adjust end to be at last full stop (inclusive)
#             actual_end = start + last_full_stop + 1
#             chunks.append(text[start:actual_end])
#             # Next chunk starts right after the last full stop
#             start = actual_end
#         else:
#             # If no full stop found, just take the chunk as is
#             chunks.append(temp_chunk)
#             start += chunk_size - overlap

#         # Prevent infinite loop in edge case where start does not advance
#         if last_full_stop == -1 and end == text_length:
#             break

#     return chunks
def chunk_book_text(text, chunk_size=2000, chunk_overlap=400):

    # Initialize the RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", ". "]
    )

    # Split the text into chunks
    raw_chunks = text_splitter.split_text(text)

    # Post-process chunks
    chunks = []
    for chunk in raw_chunks:
        cleaned_chunk = chunk.strip()                        # Remove leading/trailing whitespace
        cleaned_chunk = re.sub(r'\n+', ' ', cleaned_chunk)   # Replace all newlines with space
        cleaned_chunk = re.sub(r'^[.,;:!?\s]+', '', cleaned_chunk)  # Remove punctuation/space at start
        
        if cleaned_chunk:
            chunks.append(cleaned_chunk)

    return chunks

# Build structured JSON chunks
structured_chunks = []

for chapter_type, chapter_title, chapter_content in matches:
    ref = f"{BOOK_NAME} -> {chapter_type.strip()} -> {chapter_title.strip()}"
    clean_content = re.sub(r'\s+', ' ', chapter_content).strip()
    
    split_chunks = chunk_book_text(clean_content, CHUNK_SIZE, CHUNK_OVERLAP)
    
    for chunk in split_chunks:
        structured_chunks.append({
            "chunk": chunk,
            "ref": ref
        })

# Save JSON
with open('final_chunks(1).json', 'w', encoding='utf-8') as json_file:
    json.dump(structured_chunks, json_file, ensure_ascii=False, indent=2)

print(f"✅ Successfully created {len(structured_chunks)} properly connected chunks.")
