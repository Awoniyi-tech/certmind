"""
embed_knowledge_base.py

Reads the master_datacom_core.md document, splits it into chunks using
Markdown header boundaries, and embeds each chunk into a fresh ChromaDB
vector database.

Usage:
    cd certmind/backend
    venv\Scripts\activate
    python embed_knowledge_base.py
"""

import os
import re
import shutil
import sys
import time
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).resolve().parent
DATA_DIR     = BASE_DIR / "data"
MASTER_DOC   = DATA_DIR / "master_datacom_core.md"
CHROMA_DIR   = DATA_DIR / "chroma_db"
ARCHIVE_DIR  = DATA_DIR / "archive"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "langchain"   # Same name the RAG service expects


def archive_old_data():
    """Move old chroma_db to archive folder instead of deleting it."""
    if CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir()):
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        archive_dest = ARCHIVE_DIR / f"chroma_db_old_{timestamp}"
        print(f"  Archiving old ChromaDB to: {archive_dest}")
        shutil.move(str(CHROMA_DIR), str(archive_dest))
    else:
        print("  No old ChromaDB to archive.")

    # Also archive the old converted document if it exists
    old_doc = DATA_DIR / "converted_document_clean.md"
    if old_doc.exists():
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        archive_dest = ARCHIVE_DIR / f"converted_document_clean_old_{time.strftime('%Y%m%d_%H%M%S')}.md"
        print(f"  Archiving old document to: {archive_dest}")
        shutil.move(str(old_doc), str(archive_dest))


def split_markdown_by_headers(text, max_chunk_size=1500):
    """Split markdown text into chunks based on headers.
    
    Strategy:
    - Split on ## headers (H2) as primary boundaries
    - If a chunk is still too large, split on ### headers (H3)
    - Each chunk gets metadata with its topic path (H1 > H2 > H3)
    - This ensures the RAG system can find content by topic name
    """
    chunks = []
    
    # Track the current H1 heading (main topic like "BGP Basics")
    current_h1 = "General"
    current_h2 = ""
    current_h3 = ""
    
    # Split on H2 headers first (match ## but NOT ### or # alone)
    sections = re.split(r'(?=^## (?!#))', text, flags=re.MULTILINE)
    
    for section in sections:
        if not section.strip():
            continue
        
        # Scan for H1 headers ANYWHERE in this section using re.search
        # Use (?!#) negative lookahead so we don't match ## or ###
        h1_match = re.search(r'^# (?!#)(.+)', section, re.MULTILINE)
        if h1_match:
            current_h1 = h1_match.group(1).strip()
        
        # Check if this section starts with an H2
        h2_match = re.match(r'^## (?!#)(.+)', section)
        if h2_match:
            current_h2 = h2_match.group(1).strip()
        
        # If the section is small enough, keep it as one chunk
        if len(section) <= max_chunk_size:
            if section.strip():
                topic = current_h1
                if current_h2:
                    topic += f" > {current_h2}"
                chunks.append({
                    "text": section.strip(),
                    "metadata": {
                        "topic": topic,
                        "h1": current_h1,
                        "h2": current_h2,
                        "source": "master_datacom_core.md",
                        "vendor": "huawei",
                    }
                })
        else:
            # Section is too large - split further on H3 headers
            subsections = re.split(r'(?=^### )', section, flags=re.MULTILINE)
            for subsec in subsections:
                if not subsec.strip():
                    continue
                
                h3_match = re.match(r'^### (.+)', subsec)
                if h3_match:
                    current_h3 = h3_match.group(1).strip()
                
                # If still too large, split by paragraphs
                if len(subsec) > max_chunk_size:
                    paragraphs = subsec.split('\n\n')
                    current_chunk = ""
                    for para in paragraphs:
                        if len(current_chunk) + len(para) + 2 > max_chunk_size and current_chunk:
                            topic = current_h1
                            if current_h2:
                                topic += f" > {current_h2}"
                            if current_h3:
                                topic += f" > {current_h3}"
                            chunks.append({
                                "text": current_chunk.strip(),
                                "metadata": {
                                    "topic": topic,
                                    "h1": current_h1,
                                    "h2": current_h2,
                                    "h3": current_h3,
                                    "source": "master_datacom_core.md",
                                    "vendor": "huawei",
                                }
                            })
                            current_chunk = para
                        else:
                            current_chunk += "\n\n" + para if current_chunk else para
                    
                    if current_chunk.strip():
                        topic = current_h1
                        if current_h2:
                            topic += f" > {current_h2}"
                        if current_h3:
                            topic += f" > {current_h3}"
                        chunks.append({
                            "text": current_chunk.strip(),
                            "metadata": {
                                "topic": topic,
                                "h1": current_h1,
                                "h2": current_h2,
                                "h3": current_h3,
                                "source": "master_datacom_core.md",
                                "vendor": "huawei",
                            }
                        })
                else:
                    topic = current_h1
                    if current_h2:
                        topic += f" > {current_h2}"
                    if current_h3:
                        topic += f" > {current_h3}"
                    chunks.append({
                        "text": subsec.strip(),
                        "metadata": {
                            "topic": topic,
                            "h1": current_h1,
                            "h2": current_h2,
                            "h3": current_h3,
                            "source": "master_datacom_core.md",
                            "vendor": "huawei",
                        }
                    })
    
    return chunks


def embed_chunks(chunks):
    """Create a fresh ChromaDB and embed all chunks."""
    import chromadb
    from sentence_transformers import SentenceTransformer
    
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    # Create fresh ChromaDB directory
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"  Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
    
    print(f"  Creating fresh ChromaDB at: {CHROMA_DIR}")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    
    # Delete collection if it exists (clean start)
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"   Deleted existing '{COLLECTION_NAME}' collection")
    except Exception:
        pass
    
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    
    print(f"  Embedding {len(chunks)} chunks...")
    
    # Process in batches of 100 for efficiency
    batch_size = 100
    total_embedded = 0
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        
        texts      = [c["text"] for c in batch]
        metadatas  = [c["metadata"] for c in batch]
        ids        = [f"chunk_{i + j}" for j in range(len(batch))]
        
        # Generate embeddings
        embeddings = model.encode(texts, normalize_embeddings=True).tolist()
        
        # Add to ChromaDB
        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        
        total_embedded += len(batch)
        print(f"   Embedded {total_embedded}/{len(chunks)} chunks")
    
    print(f"\n  Done! {total_embedded} chunks embedded into ChromaDB.")
    print(f"   Database location: {CHROMA_DIR}")
    
    # Print topic distribution
    topics = {}
    for c in chunks:
        h1 = c["metadata"]["h1"]
        topics[h1] = topics.get(h1, 0) + 1
    
    print(f"\n  Topic distribution ({len(topics)} topics):")
    for topic, count in sorted(topics.items(), key=lambda x: -x[1]):
        print(f"   {count:3d} chunks - {topic}")


def main():
    print("=" * 60)
    print("  CertMind Knowledge Base Embedder")
    print("=" * 60)
    print()
    
    # Check master document exists
    if not MASTER_DOC.exists():
        print(f"  ERROR: Master document not found: {MASTER_DOC}")
        print("   Run the combine script first.")
        sys.exit(1)
    
    file_size = MASTER_DOC.stat().st_size
    print(f"  Master document: {MASTER_DOC}")
    print(f"   Size: {file_size / 1024:.1f} KB")
    
    # Step 1: Archive old data
    print("\n--- Step 1: Archive old data ---")
    archive_old_data()
    
    # Step 2: Read and split the document
    print("\n--- Step 2: Split document into chunks ---")
    text = MASTER_DOC.read_text(encoding="utf-8")
    chunks = split_markdown_by_headers(text)
    print(f"   Created {len(chunks)} chunks from the master document")
    
    # Show some stats
    sizes = [len(c["text"]) for c in chunks]
    print(f"   Avg chunk size: {sum(sizes) // len(sizes)} chars")
    print(f"   Min chunk size: {min(sizes)} chars")
    print(f"   Max chunk size: {max(sizes)} chars")
    
    # Step 3: Embed into ChromaDB
    print("\n--- Step 3: Embed chunks into ChromaDB ---")
    embed_chunks(chunks)
    
    print("\n" + "=" * 60)
    print("  Knowledge base is ready!")
    print("  The RAG system will now use your new, clean data.")
    print("=" * 60)


if __name__ == "__main__":
    main()

