import os
from pathlib import Path

import aiosqlite

DB_PATH = Path(os.getenv("DB_PATH", "./data/certmind.db"))


async def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        # ---------------------------------------------------------------
        # Core tables — CREATE IF NOT EXISTS is safe for fresh installs.
        # For existing databases, the ALTER TABLE migrations below add
        # any columns that were introduced after initial release.
        # ---------------------------------------------------------------
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id          TEXT PRIMARY KEY,
                email       TEXT UNIQUE NOT NULL,
                password    TEXT NOT NULL,
                name        TEXT NOT NULL,
                created_at  TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS certifications (
                id          TEXT PRIMARY KEY,
                vendor      TEXT NOT NULL,
                level       TEXT NOT NULL,
                name        TEXT NOT NULL,
                code        TEXT NOT NULL,
                created_at  TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS question_banks (
                id              TEXT PRIMARY KEY,
                cert_id         TEXT NOT NULL,
                source_type     TEXT NOT NULL,
                source_name     TEXT,
                total_questions INTEGER DEFAULT 0,
                created_at      TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (cert_id) REFERENCES certifications(id)
            );

            CREATE TABLE IF NOT EXISTS questions (
                id              TEXT PRIMARY KEY,
                bank_id         TEXT NOT NULL,
                cert_id         TEXT NOT NULL,
                type            TEXT NOT NULL,
                topic           TEXT,
                question        TEXT NOT NULL,
                options         TEXT NOT NULL,
                answer_key      TEXT NOT NULL,
                explanation     TEXT,
                sources         TEXT,
                difficulty      TEXT DEFAULT 'medium',
                created_at      TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (bank_id) REFERENCES question_banks(id)
            );

            CREATE TABLE IF NOT EXISTS exam_sessions (
                id              TEXT PRIMARY KEY,
                cert_id         TEXT NOT NULL,
                bank_id         TEXT,
                session_type    TEXT NOT NULL,
                total_questions INTEGER NOT NULL,
                status          TEXT DEFAULT 'active',
                started_at      TEXT DEFAULT (datetime('now')),
                completed_at    TEXT,
                score           REAL,
                time_taken_s    INTEGER
            );

            CREATE TABLE IF NOT EXISTS attempts (
                id              TEXT PRIMARY KEY,
                session_id      TEXT NOT NULL,
                question_id     TEXT NOT NULL,
                selected        TEXT NOT NULL,
                is_correct      INTEGER NOT NULL,
                confidence      TEXT,
                time_taken_s    INTEGER,
                ai_explanation  TEXT,
                ai_sources      TEXT,
                created_at      TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES exam_sessions(id),
                FOREIGN KEY (question_id) REFERENCES questions(id)
            );

            CREATE TABLE IF NOT EXISTS wrong_questions (
                id          TEXT PRIMARY KEY,
                question_id TEXT NOT NULL,
                session_id  TEXT NOT NULL,
                cert_id     TEXT NOT NULL,
                topic       TEXT,
                times_wrong INTEGER DEFAULT 1,
                last_seen   TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (question_id) REFERENCES questions(id)
            );

            CREATE TABLE IF NOT EXISTS ai_cache (
                cache_key   TEXT PRIMARY KEY,
                cache_type  TEXT NOT NULL,
                content     TEXT NOT NULL,
                created_at  TEXT DEFAULT (datetime('now')),
                expires_at  TEXT,
                hit_count   INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS study_streaks (
                id          TEXT PRIMARY KEY,
                user_id     TEXT NOT NULL,
                date        TEXT NOT NULL,
                activity    TEXT NOT NULL,
                created_at  TEXT DEFAULT (datetime('now')),
                UNIQUE(user_id, date)
            );

            CREATE INDEX IF NOT EXISTS idx_questions_cert
                ON questions(cert_id);
            CREATE INDEX IF NOT EXISTS idx_questions_bank
                ON questions(bank_id);
            CREATE INDEX IF NOT EXISTS idx_attempts_session
                ON attempts(session_id);
            CREATE INDEX IF NOT EXISTS idx_wrong_cert
                ON wrong_questions(cert_id);
            CREATE INDEX IF NOT EXISTS idx_cache_type
                ON ai_cache(cache_type);

            INSERT OR IGNORE INTO certifications (id, vendor, level, name, code) VALUES
                ('hcip-datacom', 'Huawei', 'HCIP', 'HCIP Datacom Core', 'H12-821'),
                ('hcip-security','Huawei', 'HCIP', 'HCIP Security',     'H12-721'),
                ('hcia-datacom', 'Huawei', 'HCIA', 'HCIA Datacom',      'H12-811'),
                ('ccna',         'Cisco',  'Associate', 'CCNA',         '200-301'),
                ('ccnp-ent',     'Cisco',  'Professional','CCNP Enterprise','350-401'),
                ('aws-saa',      'AWS',    'Associate', 'AWS Solutions Architect', 'SAA-C03');
        """)

        # ---------------------------------------------------------------
        # Migrations — add columns that were introduced after v1.
        # Each ALTER TABLE is wrapped in try/except so it silently skips
        # if the column already exists.
        # ---------------------------------------------------------------
        migrations = [
            "ALTER TABLE attempts ADD COLUMN ai_explanation TEXT",
            "ALTER TABLE attempts ADD COLUMN ai_sources TEXT",
            "ALTER TABLE questions ADD COLUMN sources TEXT",
            "ALTER TABLE questions ADD COLUMN needs_review INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE question_banks ADD COLUMN explanation_progress TEXT DEFAULT NULL",
            "ALTER TABLE question_banks ADD COLUMN user_id TEXT",
            "ALTER TABLE exam_sessions ADD COLUMN user_id TEXT",
            "ALTER TABLE wrong_questions ADD COLUMN user_id TEXT",
        ]
        for stmt in migrations:
            try:
                await db.execute(stmt)
            except Exception:
                pass  # column already exists — nothing to do

        # Create indexes for the new user_id columns (safe to re-run)
        index_migrations = [
            "CREATE INDEX IF NOT EXISTS idx_wrong_user ON wrong_questions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_user ON exam_sessions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_banks_user ON question_banks(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_streaks_user ON study_streaks(user_id)",
        ]
        for stmt in index_migrations:
            try:
                await db.execute(stmt)
            except Exception:
                pass

        await db.commit()


async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        db.row_factory = aiosqlite.Row
        yield db

