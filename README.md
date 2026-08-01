# CertMind — AI Certification Learning Platform

A professional exam preparation platform for network engineers studying
Huawei HCIP/HCIA, Cisco, AWS and other certifications.

---

## Project Structure

```
certmind/
├── backend/     FastAPI + SQLite + ChromaDB
└── frontend/    React + Tailwind + Vite
```

---

## Prerequisites

- Python 3.11+
- Node.js 22+
- Your Google AI Studio API key (free at https://aistudio.google.com)

---

## BACKEND SETUP

### Step 1 — Open terminal, go to backend folder

```
cd C:\Users\User\Desktop\certmind\backend
```

### Step 2 — Create virtual environment

```
python -m venv venv
venv\Scripts\activate
```

### Step 3 — Install dependencies

```
pip install -r requirements.txt
```

### Step 4 — Create your .env file

```
copy .env.example .env
notepad .env
```

Set your Google API key:
```
GOOGLE_API_KEY=your_actual_key_here
NETMIND_PATH=C:\Users\User\Desktop\netmind
```

The NETMIND_PATH points to your existing netmind project
so CertMind can reuse the ChromaDB knowledge base you already built.

### Step 5 — Run the backend

```
uvicorn main:app --reload --port 8000
```

Backend runs at: http://localhost:8000
API docs at:     http://localhost:8000/docs

---

## FRONTEND SETUP

### Step 1 — Open a NEW terminal, go to frontend folder

```
cd C:\Users\User\Desktop\certmind\frontend
```

### Step 2 — Install dependencies

```
npm install
```

### Step 3 — Run the frontend

```
npm run dev
```

Frontend runs at: http://localhost:5173

---

## HOW TO USE

1. Open http://localhost:5173 in your browser
2. The sidebar shows all sections: Dashboard, Learn, Practice, Exam, etc.
3. First go to Dump Manager and upload a Huawei exam dump PDF
4. Go to Exam Simulation, choose your certification and question count
5. Start the exam — answer questions, get immediate feedback and explanations

---

## CONNECTING TO YOUR EXISTING KNOWLEDGE BASE

CertMind reuses the ChromaDB vector database you built in NetMind.
Make sure NETMIND_PATH in your .env points to your netmind folder.

Your converted_document_clean.md is already indexed there.
No need to re-process anything.

---

## SYSTEM ARCHITECTURE & HOW THINGS WORK

This section documents how the system works internally, so any developer
or AI model working on this codebase can understand the full flow.

### Architecture Overview

```
Browser (React + Vite)
     |
     | HTTP requests (via axios, JWT auth)
     v
FastAPI Backend (port 8000)
     |
     |-- SQLite DB       question banks, questions, attempts, analytics
     |-- ChromaDB        certification study materials (from netmind)
     |-- Gemini Flash    explanations, tutor chat, learn content, question generation
     |-- PyMuPDF         PDF question extraction from exam dumps
```

The LLM NEVER decides correct answers.
Correct answers come from the question bank (dump PDFs or generated).
The LLM only explains, teaches, and coaches.

---

### Key Principle: Pre-Generated Explanations (Instant Display)

**Explanations are NEVER generated on-the-fly when a user clicks an answer.**

Instead, explanations are generated BEFORE the exam/practice session starts:

1. **For AI-generated questions** (`/api/rag/generate`):
   - The RAG service generates questions from ChromaDB context
   - Then `ensure_explanations()` generates explanations for ALL questions
   - Both questions and explanations are stored in the `questions` table
   - When the session starts, questions already have explanations attached

2. **For dump bank questions** (`/api/dumps/{bank_id}/process`):
   - Questions are extracted from the PDF via PyMuPDF
   - A background task (`_generate_explanations_background`) generates explanations
   - Explanations are written to the `questions` table as they complete
   - The dump bank shows progress (e.g., "15/60") in the UI

3. **At session start** (`/api/exam/start`):
   - Questions are loaded from the DB
   - Any questions still missing explanations get them generated **inline**
   - This means the "Start" button may take a moment, but once loaded,
     ALL explanations are pre-populated and display **instantly**

4. **When user clicks an answer** (frontend `ExamRunner.jsx`):
   - The answer is submitted to `/api/exam/{session_id}/answer`
   - The explanation is already on the question object (`q.explanation`)
   - It displays immediately — NO network call, NO loading spinner

---

### Question Sources

There are two ways to get questions:

#### 1. AI-Generated Questions
- User goes to Exam Setup or Practice → selects "Generate Questions" tab
- Frontend calls `POST /api/rag/generate` with cert_id, topic, count
- Backend uses ChromaDB RAG to generate questions via Gemini Flash
- Questions + explanations are stored in a new question bank
- The bank's `source_type = 'generated'`

#### 2. Dump Bank Questions (from PDF)
- User goes to Dump Manager → uploads a PDF exam dump
- Frontend calls `POST /api/dumps/upload`, then `POST /api/dumps/{bank_id}/process`
- Backend extracts questions from PDF using PyMuPDF + AI parsing
- Questions are stored; explanations are generated in background
- The bank's `source_type = 'dump'`

Both Exam Setup and Practice Mode have tabs to choose between these sources.

---

### Practice Mode vs Exam Mode

Both modes use the same underlying system (same `ExamRunner.jsx` component):

- **Practice Mode** (`session_type = 'practice'`):
  - User picks "Generate" or "From Dump Bank"
  - Selects topic, question type, count
  - Gets immediate feedback + explanation after each answer
  
- **Exam Mode** (`session_type = 'exam'`):
  - Same source selection (Generate or Dump Bank)
  - Full exam simulation with timer
  - Gets immediate feedback + explanation after each answer

---

### Database Schema (SQLite)

Key tables in `backend/data/certmind.db`:

| Table | Purpose |
|-------|---------|
| `users` | User accounts (email, hashed password, name) |
| `certifications` | Available certs (HCIP, CCNA, etc.) |
| `question_banks` | Groups of questions (from dumps or AI generation) |
| `questions` | Individual questions with options, answer_key, **explanation**, sources |
| `exam_sessions` | Each exam/practice session (score, time, status) |
| `attempts` | Each answer attempt within a session |
| `wrong_questions` | Tracks questions the user got wrong for review |
| `ai_cache` | Caches LLM responses to avoid duplicate API calls |
| `study_streaks` | Daily activity tracking for streak feature |

Important columns in `questions`:
- `explanation` — Pre-generated explanation text (stored before session starts)
- `sources` — JSON array of source document references from ChromaDB
- `bank_id` — Links to the question bank
- `answer_key` — The correct answer(s), stored as string or JSON array

---

### API Endpoints

#### Auth (`/api/auth/`)
- `POST /register` — Create account
- `POST /login` — Get JWT token
- `GET /me` — Current user info

#### Exam (`/api/exam/`)
- `POST /start` — Start exam/practice session (pre-generates missing explanations inline)
- `POST /{session_id}/answer` — Submit answer for a question
- `POST /{session_id}/finish` — End session, calculate score
- `GET /{session_id}/replay` — Get full session replay with explanations
- `GET /sessions` — List past sessions

#### RAG (`/api/rag/`)
- `POST /generate` — Generate fresh questions with explanations
- `POST /explain` — Get explanation for a question (used for backfill only)
- `POST /learn` — Get study material on a topic
- `POST /tutor` — AI tutor chat
- `POST /backfill` — Backfill missing explanations for existing questions
- `GET /certifications` — List available certifications

#### Dumps (`/api/dumps/`)
- `POST /upload` — Upload PDF dump file
- `POST /{bank_id}/process` — Extract questions from uploaded PDF
- `GET /{bank_id}/status` — Check explanation generation progress
- `GET /` — List dump banks
- `PUT /{bank_id}/save` — Save a generated bank as a dump
- `DELETE /{bank_id}` — Delete a question bank

#### Analytics (`/api/analytics/`)
- `GET /overview` — Dashboard stats
- `GET /topics` — Per-topic accuracy
- `GET /history` — Session history
- `GET /accuracy-trend` — Score trend over time
- `GET /confidence` — Confidence vs accuracy analysis
- `GET /recommendations` — AI study recommendations
- `GET /streak` — Study streak data

#### Questions (`/api/questions/`)
- `GET /` — List questions with filters
- `GET /topics` — Get available topics
- `GET /wrong` — Get user's wrong questions for review

---

### Frontend Pages

| Page | File | Purpose |
|------|------|---------|
| Dashboard | `Dashboard.jsx` | Overview stats, streaks, recent sessions |
| Exam Setup | `ExamSetup.jsx` | Configure exam (source, count, type) |
| Practice | `Practice.jsx` | Configure practice (source, topic, count) |
| Exam Runner | `ExamRunner.jsx` | The actual exam/practice UI with instant explanations |
| Exam Results | `ExamResults.jsx` | Score breakdown after finishing |
| Dump Manager | `Dumps.jsx` | Upload and manage PDF dumps |
| Learn | `Learn.jsx` | Study topics with AI-generated content |
| AI Tutor | `AITutor.jsx` | Chat with AI tutor |
| Analytics | `Analytics.jsx` | Detailed performance analytics |
| Wrong Questions | `WrongQuestions.jsx` | Review questions you got wrong |
| Login | `Login.jsx` | Auth page (login/register) |

---

### Key Services

#### `backend/services/rag_service.py`
- `explain()` — Personalized explanation (knows what student answered)
- `explain_generic()` — Generic pre-generated explanation (before anyone answers)
- `generate_questions()` — Generate fresh questions from ChromaDB RAG
- `ensure_explanations()` — Batch-generate explanations for a list of questions
- `background_generate_explanations()` — Background task for dump processing
- `learn_topic()` — Generate study material
- `tutor_chat()` — AI tutor conversation

#### `backend/services/dump_service.py`
- `extract_questions_from_pdf()` — Parse PDF dumps into structured questions

---

### Important Design Decisions

1. **No on-demand LLM calls during exams** — All explanations are pre-generated
   and stored in the DB before the session starts. This ensures instant display.

2. **Explanations stored in `questions` table** — Not in a separate table. The
   `explanation` column on each question row holds the pre-generated text.

3. **Generated banks are hidden from Dump Manager** — Banks with
   `source_type = 'generated'` don't appear in the dump list. Only
   `source_type = 'dump'` banks show up. Users can save generated banks.

4. **User isolation** — All data is scoped by `user_id`. Users only see their
   own banks, sessions, and analytics.

5. **ChromaDB reuse** — CertMind reuses the ChromaDB from the NetMind project
   (via NETMIND_PATH / CHROMA_PATH env vars) instead of maintaining its own.

---

## DEPLOYMENT

### Frontend to Netlify (free)

```
cd frontend
npm run build
```

Drag the `dist` folder to https://app.netlify.com/drop

### Backend to Railway (free)

1. Push backend folder to a GitHub repo
2. Go to https://railway.app
3. New Project → Deploy from GitHub
4. Add environment variables from your .env
5. Done — Railway gives you a live URL

Update your frontend vite.config.js proxy target to the Railway URL.

---

## LAST UPDATED

**Date:** 2026-08-01

**Recent Changes:**
- Pre-generated explanations system — explanations are now generated inline
  before the session starts (not in background). Instant display on answer click.
- Practice mode now has "Generate Questions" and "From Dump Bank" tabs
  (previously had no source selection, which was confusing).
- Fixed undefined `n` variable bug in Practice.jsx that would crash practice mode.
- Removed on-demand `/api/rag/explain` calls from ExamRunner — no longer needed.
- Removed background `_pregenerate_explanations_bg` from exam.py — replaced with
  inline `ensure_explanations()` call in the start_exam endpoint.
