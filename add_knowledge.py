
from pathlib import Path
import argparse
import hashlib
import re
import unicodedata

import chromadb
import requests
from pypdf import PdfReader


# =========================================================
# 1. ตั้งค่าระบบ
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

KNOWLEDGE_DIR = BASE_DIR / "knowledge"
DB_DIR = BASE_DIR / "chroma_db"

OLLAMA_URL = "http://127.0.0.1:11434"
EMBED_MODEL = "bge-m3"

COLLECTION_NAME = "knowledge"

SUPPORTED = {".txt", ".md", ".pdf"}

CHUNK_SIZE = 900
CHUNK_OVERLAP = 120
MIN_CHUNK = 40

# เปลี่ยน Version เมื่อปรับวิธีแบ่งข้อความ
CHUNKER_VERSION = f"v3-heading-{CHUNK_SIZE}-{CHUNK_OVERLAP}"

BATCH_SIZE = 16

KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(path=str(DB_DIR))


# =========================================================
# 2. จัดการฐานข้อมูล
# =========================================================

def get_collection(rebuild=False):

    if rebuild:
        print("คำเตือน: กำลังสร้างฐานความรู้ใหม่ทั้งหมด")

        try:
            client.delete_collection(COLLECTION_NAME)
            print("ลบ Collection เดิมเรียบร้อย")
        except Exception:
            pass

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


# =========================================================
# 3. อ่านไฟล์ความรู้
# =========================================================

def read_text_file(path):

    raw = path.read_bytes()

    for encoding in ("utf-8-sig", "cp874", "tis-620"):

        try:
            return raw.decode(encoding)

        except UnicodeDecodeError:
            continue

    return raw.decode("utf-8", errors="replace")


def read_file(path):

    if path.suffix.lower() == ".pdf":

        reader = PdfReader(str(path))

        pages = []

        for page_number, page in enumerate(reader.pages, start=1):

            page_text = page.extract_text() or ""

            if page_text.strip():
                pages.append(
                    f"[หน้า {page_number}]\n{page_text}"
                )

        return "\n\n".join(pages)

    return read_text_file(path)


# =========================================================
# 4. แบ่งข้อความโดยรักษาหัวข้อ Markdown
# =========================================================

def split_long_text(text):

    result = []

    while len(text) > CHUNK_SIZE:

        window = text[:CHUNK_SIZE]

        # พยายามตัดตรงช่องว่างหรือจุดสิ้นสุดประโยค
        boundaries = [
            match.end()
            for match in re.finditer(
                r"[\s。！？.!?;；]",
                window
            )
        ]

        valid_boundaries = [
            position
            for position in boundaries
            if position >= int(CHUNK_SIZE * 0.60)
        ]

        cut = (
            valid_boundaries[-1]
            if valid_boundaries
            else CHUNK_SIZE
        )

        piece = text[:cut].strip()

        if piece:
            result.append(piece)

        text = text[cut:].strip()

    if text:
        result.append(text)

    return result


def split_text(text):

    if not text:
        return []

    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    blocks = []

    current_heading = "บทนำ"
    paragraph_lines = []

    def flush_paragraph():

        nonlocal paragraph_lines

        if not paragraph_lines:
            return

        paragraph = "\n".join(
            paragraph_lines
        ).strip()

        if paragraph:

            blocks.append(
                (current_heading, paragraph)
            )

        paragraph_lines = []

    # อ่านทีละบรรทัด และตรวจหัวข้อ Markdown
    for raw_line in text.splitlines():

        line = re.sub(
            r"[ \t]+",
            " ",
            raw_line
        ).strip()

        if not line:

            flush_paragraph()
            continue

        heading_match = re.match(
            r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$",
            line
        )

        if heading_match:

            flush_paragraph()

            current_heading = heading_match.group(1).strip()

            continue

        paragraph_lines.append(line)

    flush_paragraph()

    # รวมย่อหน้าเป็น Chunk
    raw_chunks = []
    current_chunk = ""

    for heading, paragraph in blocks:

        block = (
            f"หัวข้อ: {heading}\n{paragraph}"
        )

        pieces = split_long_text(block)

        for piece in pieces:

            if len(piece) > CHUNK_SIZE:

                if current_chunk:
                    raw_chunks.append(current_chunk)
                    current_chunk = ""

                raw_chunks.append(piece)
                continue

            if (
                current_chunk
                and len(current_chunk) + len(piece) + 2 > CHUNK_SIZE
            ):

                raw_chunks.append(current_chunk)

                current_chunk = piece

            else:

                current_chunk = (
                    f"{current_chunk}\n\n{piece}"
                    if current_chunk
                    else piece
                )

    if current_chunk:
        raw_chunks.append(current_chunk)

    # เพิ่ม Overlap เพื่อรักษาบริบทระหว่าง Chunk
    final_chunks = []

    for index, chunk in enumerate(raw_chunks):

        if index > 0:

            previous_tail = raw_chunks[index - 1][
                -CHUNK_OVERLAP:
            ]

            chunk = previous_tail + "\n" + chunk

        if len(chunk.strip()) >= MIN_CHUNK:
            final_chunks.append(chunk.strip())

    return final_chunks


# =========================================================
# 5. สร้าง Embeddings ด้วย Ollama
# =========================================================

def embed_texts(texts):

    response = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={
            "model": EMBED_MODEL,
            "input": texts,
        },
        timeout=300,
    )

    response.raise_for_status()

    embeddings = response.json().get("embeddings")

    if not embeddings:
        raise RuntimeError(
            "Ollama ไม่ได้ส่ง Embeddings กลับมา"
        )

    if len(embeddings) != len(texts):
        raise RuntimeError(
            "จำนวน Embeddings ไม่ตรงกับจำนวนข้อความ"
        )

    return embeddings


# =========================================================
# 6. ตรวจสอบไฟล์และ Hash
# =========================================================

def file_hash(path):

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def make_document_id(source, digest, chunk_index):

    raw_id = (
        f"{source}|{digest}|{CHUNKER_VERSION}|{chunk_index}"
    )

    return hashlib.sha256(
        raw_id.encode("utf-8")
    ).hexdigest()


def get_source_data(collection, source):

    return collection.get(
        where={"source": source},
        include=["metadatas"],
    )


def is_up_to_date(
    collection,
    source,
    digest,
    expected_chunks
):

    found = get_source_data(collection, source)

    metadatas = found.get("metadatas") or []

    if len(metadatas) != expected_chunks:
        return False

    return all(
        metadata
        and metadata.get("file_hash") == digest
        and metadata.get("chunker") == CHUNKER_VERSION
        for metadata in metadatas
    )


# =========================================================
# 7. ลบข้อมูลเก่าหลังนำเข้าข้อมูลใหม่สำเร็จเท่านั้น
# =========================================================

def delete_old_chunks(collection, source, new_ids):

    old_data = get_source_data(collection, source)

    old_ids = old_data.get("ids") or []

    new_id_set = set(new_ids)

    stale_ids = [
        old_id
        for old_id in old_ids
        if old_id not in new_id_set
    ]

    for start in range(0, len(stale_ids), 500):

        collection.delete(
            ids=stale_ids[start:start + 500]
        )

    if stale_ids:

        print(
            f"ลบ Chunk เวอร์ชันเก่าของ {source}: "
            f"{len(stale_ids)} ส่วน"
        )


# =========================================================
# 8. นำเข้าไฟล์หนึ่งไฟล์
# =========================================================

def ingest_file(collection, path, dry_run=False):

    relative_path = path.relative_to(
        KNOWLEDGE_DIR
    ).as_posix()

    digest = file_hash(path)

    text = read_file(path)

    chunks = split_text(text)

    if not chunks:

        print(
            f"ข้ามไฟล์ไม่มีข้อความ: {relative_path}"
        )

        return 0

    if dry_run:

        print(
            f"[ตรวจสอบ] {relative_path} "
            f"-> {len(chunks)} Chunks"
        )

        return len(chunks)

    # ไม่ต้องนำเข้าใหม่หากไฟล์ไม่มีการเปลี่ยนแปลง
    if is_up_to_date(
        collection,
        relative_path,
        digest,
        len(chunks)
    ):

        print(
            f"ไม่มีการเปลี่ยนแปลง ข้าม: {relative_path}"
        )

        return 0

    title = path.stem

    path_parts = relative_path.split("/")

    category = (
        path_parts[0]
        if len(path_parts) > 1
        else "ทั่วไป"
    )

    # เตรียม ID และ Metadata
    new_ids = [
        make_document_id(
            relative_path,
            digest,
            index
        )
        for index in range(len(chunks))
    ]

    metadatas = [
        {
            "source": relative_path,
            "title": title,
            "category": category,
            "chunk": index,
            "file_hash": digest,
            "chunker": CHUNKER_VERSION,
        }
        for index in range(len(chunks))
    ]

    # -----------------------------------------------------
    # ขั้นตอนสำคัญ:
    # สร้าง Embeddings ให้ครบก่อนแตะข้อมูลเก่า
    # -----------------------------------------------------

    all_embeddings = []

    for start in range(0, len(chunks), BATCH_SIZE):

        batch = chunks[start:start + BATCH_SIZE]

        # เพิ่มชื่อไฟล์เข้าไปในข้อความที่ใช้สร้าง Embedding
        embedding_inputs = [
            f"เอกสาร: {title}\nเนื้อหา:\n{chunk}"
            for chunk in batch
        ]

        embeddings = embed_texts(embedding_inputs)

        all_embeddings.extend(embeddings)

        print(
            f"กำลังสร้าง Embeddings: "
            f"{relative_path} "
            f"{min(start + BATCH_SIZE, len(chunks))}/{len(chunks)}"
        )

    if len(all_embeddings) != len(chunks):

        raise RuntimeError(
            "Embeddings ไม่ครบทุก Chunk"
        )

    # -----------------------------------------------------
    # นำเข้าข้อมูลใหม่
    # -----------------------------------------------------

    for start in range(0, len(chunks), BATCH_SIZE):

        end = start + BATCH_SIZE

        collection.upsert(
            ids=new_ids[start:end],
            documents=chunks[start:end],
            embeddings=all_embeddings[start:end],
            metadatas=metadatas[start:end],
        )

    # ลบข้อมูลเก่าเมื่อบันทึกข้อมูลใหม่สำเร็จครบแล้ว
    delete_old_chunks(
        collection,
        relative_path,
        new_ids
    )

    print(
        f"เพิ่มความรู้สำเร็จ: {relative_path} "
        f"({len(chunks)} Chunks)"
    )

    return len(chunks)


# =========================================================
# 9. ลบไฟล์ที่ไม่มีอยู่แล้ว (ต้องสั่งเอง)
# =========================================================

def prune_missing_sources(collection, current_sources):

    stored = collection.get(
        include=["metadatas"]
    )

    metadatas = stored.get("metadatas") or []

    stored_sources = {
        metadata.get("source")
        for metadata in metadatas
        if metadata and metadata.get("source")
    }

    missing_sources = stored_sources - current_sources

    for source in missing_sources:

        collection.delete(
            where={"source": source}
        )

        print(
            f"ลบข้อมูลของไฟล์ที่ไม่มีแล้ว: {source}"
        )


# =========================================================
# 10. เริ่มโปรแกรม
# =========================================================

def main():

    parser = argparse.ArgumentParser(
        description="Local AI Knowledge Ingestion"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="ตรวจสอบไฟล์และจำนวน Chunk โดยไม่แก้ฐานข้อมูล",
    )

    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="ลบ Collection เดิมและสร้างฐานความรู้ใหม่ทั้งหมด",
    )

    parser.add_argument(
        "--prune-missing",
        action="store_true",
        help="ลบข้อมูลของไฟล์ที่ไม่มีอยู่ใน knowledge แล้ว",
    )

    args = parser.parse_args()

    files = sorted(
        path
        for path in KNOWLEDGE_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED
    )

    if not files:

        print(
            "ยังไม่มีไฟล์ PDF, TXT หรือ MD "
            "ในโฟลเดอร์ knowledge"
        )

        return

    current_sources = {
        path.relative_to(KNOWLEDGE_DIR).as_posix()
        for path in files
    }

    if args.rebuild and args.dry_run:

        print(
            "โหมด dry-run จะไม่ลบหรือสร้างฐานข้อมูล"
        )

    collection = None

    if not args.dry_run:

        if args.rebuild:

            print("")
            print("คำเตือน: --rebuild จะลบความรู้เดิมทั้งหมด")
            print("")

        collection = get_collection(
            rebuild=args.rebuild
        )

    print("=" * 55)
    print("LOCAL AI KNOWLEDGE INGESTION")
    print("=" * 55)

    print(f"Embedding Model: {EMBED_MODEL}")
    print(f"จำนวนไฟล์ที่พบ: {len(files)}")
    print("")

    total_chunks = 0
    success_files = 0
    failed_files = []

    for path in files:

        relative_path = path.relative_to(
            KNOWLEDGE_DIR
        ).as_posix()

        try:

            count = ingest_file(
                collection,
                path,
                dry_run=args.dry_run
            )

            total_chunks += count
            success_files += 1

        except Exception as error:

            failed_files.append(relative_path)

            print(
                f"เกิดข้อผิดพลาดกับ {relative_path}: {error}"
            )

        print("-" * 55)

    # ลบไฟล์เก่าที่ถูกย้ายหรือลบออกจากโฟลเดอร์
    # เฉพาะเมื่อผู้ใช้สั่ง --prune-missing เท่านั้น

    if (
        not args.dry_run
        and args.prune_missing
    ):

        print("กำลังตรวจสอบไฟล์ที่ไม่มีแล้ว")

        prune_missing_sources(
            collection,
            current_sources
        )

    print("")
    print("=" * 55)
    print("สรุปผลการนำเข้าความรู้")
    print("=" * 55)

    print(f"ไฟล์ที่ตรวจสอบ: {len(files)}")
    print(f"ไฟล์ที่ประมวลผล: {success_files}")
    print(f"Chunk ที่เพิ่มหรือเตรียมไว้: {total_chunks}")

    if collection is not None:

        print(
            f"จำนวน Chunk ในฐานข้อมูล: {collection.count()}"
        )

    if failed_files:

        print("")
        print("ไฟล์ที่มีปัญหา:")

        for name in failed_files:
            print(f"- {name}")

    print("")
    print("เสร็จสิ้น")


if __name__ == "__main__":
    main()
