import fitz
import re
import json
from pathlib import Path

PDF_PATH = "data/postgresql-18-A4-No-TOC_removed.pdf"
OUTPUT_DIR = Path("chunks")

OUTPUT_DIR.mkdir(exist_ok=True)

# -----------------------------
# Clean Text Helper
# -----------------------------
def clean_text(t):
    # Remove soft hyphenation at line breaks (e.g. Fami-\nlies -> Families)
    t = re.sub(r"(\w+)-\n\s*(\w+)", r"\1\2", t)
    return re.sub(r"\s+", " ", t).strip()

def find_heading_offset(clean_title, page_text):
    # 1. Exact match
    pos = page_text.find(clean_title)
    if pos != -1:
        return pos
        
    # Remove numbering if search fails (e.g. "1.1. Installation" -> "Installation")
    title_no_num = re.sub(r"^([A-Za-z0-9\.\s]+)\s+", "", clean_title)
    pos = page_text.find(title_no_num)
    if pos != -1:
        return pos

    # 2. Match words prefix
    words = [w for w in re.split(r"[^\w]+", clean_title) if w]
    if not words:
        return -1
        
    # Try prefixes of varying lengths
    for l in [5, 4, 3, 2]:
        if len(words) >= l:
            prefix = " ".join(words[:l])
            pos = page_text.find(prefix)
            if pos != -1:
                return pos
                
    # Try suffix
    if len(words) >= 3:
        suffix = " ".join(words[-3:])
        pos = page_text.find(suffix)
        if pos != -1:
            return pos
            
    return -1

# -----------------------------
# Load PDF and Extract TOC
# -----------------------------
doc = fitz.open(PDF_PATH)
toc = doc.get_toc()

# -----------------------------
# Extract Page Texts
# -----------------------------
page_texts = []
for page in doc:
    page_texts.append(page.get_text())

# -----------------------------
# Slicing Chunks
# -----------------------------
chunks = []

for idx, (level, title, page_num) in enumerate(toc):
    page_idx = page_num - 1
    if page_idx >= len(doc):
        continue
        
    clean_title = clean_text(title.replace("\xa0", " "))
    
    # Start searching from the declared start page
    curr_page_text = page_texts[page_idx]
    clean_curr_page = clean_text(curr_page_text)
    
    pos = find_heading_offset(clean_title, clean_curr_page)
    # Fallback to starting at page start if not found
    start_char_offset = pos if pos != -1 else 0
    
    content_parts = []
    if pos != -1:
        content_parts.append(clean_curr_page[start_char_offset:])
    else:
        content_parts.append(clean_curr_page)
        
    # Read subsequent pages until we hit the next heading's page
    next_heading_page = len(doc)
    next_heading_title = None
    
    if idx + 1 < len(toc):
        next_heading_page = toc[idx + 1][2] - 1
        next_heading_title = clean_text(toc[idx + 1][1].replace("\xa0", " "))
        
    for p in range(page_idx + 1, min(next_heading_page, len(doc))):
        content_parts.append(clean_text(page_texts[p]))
        
    # Slice the last page up to the next heading position
    if next_heading_page < len(doc) and next_heading_page >= page_idx:
        next_page_text = clean_text(page_texts[next_heading_page])
        next_pos = find_heading_offset(next_heading_title, next_page_text)
        if next_pos != -1:
            if next_heading_page == page_idx:
                # If they are on the same page, slice the start page content correctly
                same_page_content = clean_curr_page[start_char_offset:next_pos]
                content_parts = [same_page_content]
            else:
                content_parts.append(next_page_text[:next_pos])
            
    content = " ".join(content_parts).strip()
    
    chunks.append({
        "heading": clean_title,
        "level": level,
        "content": content
    })

# -----------------------------
# Save Chunks
# -----------------------------
for idx, chunk in enumerate(chunks):
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", chunk["heading"])[:120]
    with open(OUTPUT_DIR / f"{idx:04d}_{safe_name}.json", "w", encoding="utf-8") as f:
        json.dump(chunk, f, indent=2, ensure_ascii=False)

print(f"Created {len(chunks)} clean outline-wise chunks")