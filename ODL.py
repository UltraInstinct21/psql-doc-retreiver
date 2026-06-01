import os
import subprocess
import time
import logging
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import fitz  # PyMuPDF

# ===================== CONFIG =====================
INPUT_PDF = "data/postgresql-18-A4-No-TOC.pdf"
CHUNK_DIR = "chunks"
OUTPUT_DIR = "output"
LOG_FILE = "pipeline.log"

BATCH_SIZE = 75          # pages per chunk (reduce if RAM issues)
MAX_WORKERS = 1          # keep 1 for hybrid stability
HYBRID_PORT = 5002

# ===================== LOGGING =====================
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ===================== STEP 1: SPLIT PDF (PyMuPDF) =====================
def split_pdf(input_pdf, output_dir, batch_size):
    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(input_pdf)
    total_pages = len(doc)

    chunk_paths = []

    for i in range(0, total_pages, batch_size):
        new_doc = fitz.open()

        for j in range(i, min(i + batch_size, total_pages)):
            new_doc.insert_pdf(doc, from_page=j, to_page=j)

        chunk_path = os.path.join(output_dir, f"chunk_{i}_{i+batch_size}.pdf")
        new_doc.save(chunk_path)
        new_doc.close()

        chunk_paths.append(chunk_path)
        logging.info(f"Created chunk: {chunk_path}")

    doc.close()
    return chunk_paths

# ===================== STEP 2: START HYBRID SERVER =====================
def start_hybrid_server():
    env = os.environ.copy()
    env["JAVA_TOOL_OPTIONS"] = "-Xmx4g"

    process = subprocess.Popen(
        [
            "opendataloader-pdf-hybrid",
            "--port", str(HYBRID_PORT)
        ],
        env=env
    )

    logging.info("Hybrid server started")
    time.sleep(5)
    return process

# ===================== STEP 3: PROCESS ONE CHUNK =====================
def process_chunk(chunk_path):
    try:
        logging.info(f"Processing: {chunk_path}")

        cmd = [
    "opendataloader-pdf",
    "--hybrid", "docling-fast",
    chunk_path,
    "--output-dir", OUTPUT_DIR,
    "--format", "markdown,json"
]

        subprocess.run(cmd, check=True)

        logging.info(f"Completed: {chunk_path}")
        return chunk_path, True

    except subprocess.CalledProcessError as e:
        logging.error(f"Failed: {chunk_path} | {e}")
        return chunk_path, False

# ===================== STEP 4: PROCESS ALL =====================
def process_all_chunks(chunk_paths):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    completed = set()
    if os.path.exists("completed.txt"):
        with open("completed.txt", "r") as f:
            completed = set(f.read().splitlines())

    results = []

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_chunk = {
            executor.submit(process_chunk, chunk): chunk
            for chunk in chunk_paths if chunk not in completed
        }

        for future in as_completed(future_to_chunk):
            chunk = future_to_chunk[future]
            chunk_path, success = future.result()
            results.append(success)

            if success:
                with open("completed.txt", "a") as f:
                    f.write(chunk_path + "\n")

    return results

# ===================== MAIN =====================
def main():
    logging.info("===== PIPELINE START =====")

    chunk_paths = split_pdf(INPUT_PDF, CHUNK_DIR, BATCH_SIZE)

    server = start_hybrid_server()

    try:
        results = process_all_chunks(chunk_paths)
        success_count = sum(results)
        logging.info(f"Success: {success_count}/{len(results)}")
    finally:
        server.terminate()
        logging.info("Hybrid server stopped")

    logging.info("===== PIPELINE END =====")

if __name__ == "__main__":
    main()