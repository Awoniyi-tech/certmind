"""User-owned Markdown ingestion for CertMind's personal knowledge base."""

import asyncio
import hashlib
import re
from pathlib import Path

from database.db import DB_PATH


def _chunks(text: str, size: int = 1400) -> list[str]:
    sections = re.split(r"(?=^#{1,3}\s)", text, flags=re.MULTILINE)
    result: list[str] = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        paragraphs = section.split("\n\n")
        current = ""
        for paragraph in paragraphs:
            if current and len(current) + len(paragraph) + 2 > size:
                result.append(current.strip())
                current = ""
            current = f"{current}\n\n{paragraph}".strip()
        if current:
            result.append(current)
    return result


async def index_markdown(source_id: str, user_id: str, filename: str, content: str, cert_id: str | None) -> None:
    try:
        from services.rag_service import _get_collection, _get_embed_model

        chunks = _chunks(content)
        if not chunks:
            raise ValueError("Markdown file contains no indexable text.")
        model = await asyncio.to_thread(_get_embed_model)
        embeddings = await asyncio.to_thread(model.encode, chunks, normalize_embeddings=True)
        metadata = [
            {
                "source_scope": "personal",
                "source_type": "personal",
                "user_id": user_id,
                "source_id": source_id,
                "source": filename,
                "vendor": "personal",
                "cert_id": cert_id or "",
            }
            for _ in chunks
        ]
        collection = _get_collection()
        await asyncio.to_thread(
            collection.upsert,
            ids=[f"personal_{source_id}_{index}" for index in range(len(chunks))],
            documents=chunks,
            embeddings=embeddings.tolist(),
            metadatas=metadata,
        )
        import aiosqlite
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("UPDATE knowledge_sources SET chunk_count = ?, status = 'ready', error = NULL WHERE id = ?", (len(chunks), source_id))
            await db.commit()
    except Exception as exc:
        import aiosqlite
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("UPDATE knowledge_sources SET status = 'failed', error = ? WHERE id = ?", (str(exc)[:500], source_id))
            await db.commit()


def content_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

