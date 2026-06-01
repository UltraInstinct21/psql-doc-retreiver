import fitz
import re
import json
from pathlib import Path

PDF_PATH = "data/postgresql-18-A4-No-TOC.pdf"
OUTPUT_DIR = Path("chunks")

OUTPUT_DIR.mkdir(exist_ok=True)

# -----------------------------
# Extract full text
# -----------------------------
doc = fitz.open(PDF_PATH)

text = ""
for page in doc:
    text += page.get_text()

# -----------------------------
# Heading Regex
# -----------------------------
# Matches:
# 1. Topic
# 1.1 Subtopic
# 1.1.1 Sub-subtopic

heading_pattern = re.compile(
    r"^(?P<num>(\d+\.)+\d*\.?)\s+(?P<title>.+)$",
    re.MULTILINE
)

matches = list(heading_pattern.finditer(text))

chunks = []

# -----------------------------
# Build chunks
# -----------------------------
for i, match in enumerate(matches):

    start = match.start()

    end = (
        matches[i + 1].start()
        if i + 1 < len(matches)
        else len(text)
    )

    heading = match.group().strip()
    number = match.group("num").strip(".")
    title = match.group("title").strip()

    content = text[start:end].strip()

    level = number.count(".")

    chunk = {
        "heading": heading,
        "level": level,
        "content": content
    }

    chunks.append(chunk)

# -----------------------------
# Save chunks
# -----------------------------
for idx, chunk in enumerate(chunks):

    safe_name = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        chunk["heading"]
    )[:120]

    with open(
        OUTPUT_DIR / f"{idx:04d}_{safe_name}.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(chunk, f, indent=2, ensure_ascii=False)

print(f"Created {len(chunks)} topic-wise chunks")