# Resume AI Analyzer

Resume AI Analyzer helps job seekers see how well a resume fits a specific job posting. Upload a PDF or DOCX resume, paste the job description, and get a score with a clear explanation: which required skills you demonstrate, which you only list, which are missing, whether you meet the years-of-experience and degree requirements, and what to change. The analysis runs on your own server and nothing is stored. Optional AI suggestions (via Groq) are only used when you click for them.

## Features

- **Skill matching with evidence**: Recognises 120 skills and their aliases (`k8s` → Kubernetes, `Postgres` → PostgreSQL) and shows the resume lines that prove each one.
- **Required vs. nice-to-have**: Reads the job description's headings ("Requirements", "Nice to have", "Benefits"...) so company blurbs and perks aren't treated as requirements.
- **Demonstrated vs. listed**: Skills shown in your experience or projects count fully; skills that only appear in a skills list earn partial credit, so keyword stuffing doesn't inflate the score.
- **Experience and education checks**: Adds up employment dates (overlapping roles counted once, education dates excluded), checks per-skill year requirements ("3+ years of Python"), and compares degree levels, including "or equivalent experience".
- **Actionable suggestions**: Prioritised advice on what to add or rewrite.
- **ATS readability check**: A separate score for how easily applicant tracking systems can read the file: extractable text, contact details (including email hidden in a page header), standard section headings, employment dates and date format, multi-column layouts, tables, images, icon characters, length, bullet points and quantified results. Each problem comes with a fix.
- **Robust document reading**: PyMuPDF with a pdfplumber fallback for PDFs, table-aware DOCX parsing, file-type checks based on content, and warnings for scanned or image-only resumes.
- **Optional AI suggestions (Groq)**: On request, a short assessment, draft rewrites of your bullet points, and requirements the skill list doesn't cover. Contact details are removed before anything is sent, rewrites must quote a real line from the resume, and whether each extra requirement appears in the resume is checked by text search rather than trusted from the AI. The match score stays rule-based.
- **Privacy first**: Stateless, in-memory processing with no database. Nothing leaves the server unless you request AI suggestions; then the resume text (without email, phone numbers or links) and the job description are sent to Groq.

## How the score works

| Component | Base weight | What it measures |
|---|---|---|
| Skills | 60% | Required skills (75%) and nice-to-have skills (25%). Demonstrated = 100%, only listed = 60%, related skill found = 35%, missing = 0% |
| Experience | 25% | Years of experience against each requirement in the posting |
| Education | 15% | Highest degree against the posting's requirement |

Components the posting doesn't ask about are left out and the remaining weights re-normalised. If fewer than half of the required skills match, the overall score is capped at the skills score + 20, because experience in an unrelated field shouldn't make a poor fit look good.

The **ATS readability score** is reported separately and doesn't change the match score: it describes the document, not the fit for the job. Each check is weighted by severity (critical 3, major 2, minor 1); a pass earns full credit, a warning half.

## Tech Stack

### Frontend
- **Framework**: Vue 3 (Composition API)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Build Tool**: Vite

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Document parsing**: PyMuPDF, pdfplumber, python-docx
- **Matching**: Rule-based skill taxonomy (`backend/data/skills.json`) with regex matching
- **AI (optional)**: Groq's OpenAI-compatible API over httpx (default model `openai/gpt-oss-120b`, structured JSON output)
- **Tests**: pytest

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python 3.12

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/medicophy/resume-ai-analyzer.git
    cd resume-ai-analyzer
    ```

2.  **Backend setup**
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows Git Bash: source venv/Scripts/activate
    pip install -r requirements.txt
    cp .env.example .env      # optional, defaults work for local use
    ```

3.  **Frontend setup**
    ```bash
    cd ../frontend
    npm ci
    ```

### Running the Application

1.  **Start the backend**
    ```bash
    cd backend
    python main.py
    ```
    The API is available at `http://localhost:8000` (interactive docs at `/docs`).

2.  **Start the frontend**
    ```bash
    cd frontend
    npm run dev
    ```
    The application is available at `http://localhost:5173`.

### Running the tests

```bash
cd backend
python -m pytest
```

## Configuration

Settings are read from environment variables or `backend/.env` (see `backend/.env.example`):

| Variable | Default | Purpose |
|---|---|---|
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated frontend origins allowed to call the API |
| `MAX_UPLOAD_MB` | `5` | Maximum resume file size |
| `GROQ_API_KEY` | empty | Groq API key; leave empty to turn AI suggestions off |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | Groq model used for AI suggestions |
| `GROQ_TIMEOUT_SECONDS` | `45` | How long to wait for the AI before giving up |

The frontend reads `VITE_API_URL` (default `http://localhost:8000`) from `frontend/.env` (see `frontend/.env.example`). If you serve the frontend from another address, add it to `CORS_ORIGINS`.

## API

`POST /analyze` (multipart form): `file` (PDF or DOCX) and `job_description` (text). Returns the overall score, a per-component breakdown, every job skill with its status and evidence, experience and education checks, suggestions, warnings, and the ATS readability report.

`POST /ai-review` (same form fields): optional AI review with a summary, draft rewrites and extra requirements. Returns 503 when no Groq key is configured.

`GET /`: health check; `ai_enabled` tells the frontend whether to offer AI suggestions.

## Project Structure

```
resume-ai-analyzer/
├── backend/
│   ├── main.py               # App setup (CORS, routes)
│   ├── config.py             # Settings from environment / .env
│   ├── api/routes.py         # HTTP endpoints and error handling
│   ├── models/schemas.py     # Response models
│   ├── services/
│   │   ├── extractor.py      # PDF/DOCX text extraction
│   │   ├── skills.py         # Skill taxonomy and detection
│   │   ├── jd_parser.py      # Job description requirements
│   │   ├── resume_parser.py  # Resume sections and dated roles
│   │   ├── dates.py          # Date ranges and years of experience
│   │   ├── education.py      # Degree detection
│   │   ├── matcher.py        # Skill matching with evidence
│   │   ├── scorer.py         # Scores and suggestions
│   │   ├── ats.py            # ATS readability checks
│   │   ├── ai_review.py      # Optional Groq review, redaction and validation
│   │   └── analyzer.py       # End-to-end pipeline
│   ├── data/skills.json      # Skills, aliases and related skills
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── App.vue                  # Page layout
│   │   ├── components/              # Upload form, score overview, skills,
│   │   │                            # experience/education, suggestions, AI, ATS panels
│   │   ├── composables/useAnalyze.ts  # API call, loading and error state
│   │   ├── types/analysis.ts        # Response types (mirror backend schemas)
│   │   ├── utils/format.ts          # Score colours and labels
│   │   ├── style.css                # Tailwind and shared component classes
│   │   └── main.ts
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   └── vite.config.ts
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
