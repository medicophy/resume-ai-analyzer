# Resume AI Analyzer

Resume AI Analyzer is a modern web application that leverages local NLP algorithms to help job seekers optimize their resumes for Applicant Tracking Systems (ATS). It provides instant feedback on keyword matching and skill gaps by comparing your resume against specific job descriptions, ensuring your application stands out without sending data to external APIs.

## Features

- **Smart Keyword Gap Analysis**: Extracts key skills from job descriptions and identifies missing keywords in your resume using TF-IDF vectorization.
- **Match Score Algorithm**: Calculates a precise compatibility percentage between your resume and the job role based on semantic similarity.
- **Privacy First**: All processing happens locally. No resumes or job descriptions are sent to third-party AI APIs or stored in a database.
- **Robust PDF Parsing**: Utilizes PyMuPDF to accurately extract text from complex resume layouts.
- **Modern User Interface**: A clean, intuitive, and responsive interface built with Vue 3, TypeScript, and Tailwind CSS v4.
- **Fast & Efficient**: Built on a high-performance FastAPI backend optimized for quick text analysis.

## Tech Stack

### Frontend
- **Framework**: Vue 3 (Composition API)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Build Tool**: Vite

### Backend
- **Framework**: FastAPI (Python)
- **AI/ML**: Scikit-Learn (TF-IDF, Cosine Similarity), Collections (Counter)
- **PDF Engine**: PyMuPDF (fitz)
- **Database**: None (Stateless, in-memory processing)
- **Authentication**: None (Local tool)

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python (v3.12 recommended for wheel compatibility)

### Installation

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd resume-ai-analyzer
    ```

2.  **Backend Setup**
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows Git Bash: source venv/Scripts/activate
    pip install -r requirements.txt
    ```

3.  **Frontend Setup**
    ```bash
    cd ../frontend
    npm install
    ```

### Running the Application

1.  **Start the Backend**
    ```bash
    cd backend
    python main.py
    ```
    The API will be available at `http://localhost:8000`.
    *Note: CORS is configured to allow requests from `http://localhost:5173`.*

2.  **Start the Frontend**
    ```bash
    cd ../frontend
    npm run dev
    ```
    The application will be available at `http://localhost:5173`.

## Project Structure

resume-ai-analyzer/
├── backend/ # FastAPI backend application
│ ├── venv/ # Virtual environment (ignored in git)
│ ├── main.py # Main entry point with API routes and NLP logic
│ ├── requirements.txt
│ └── .gitignore
├── frontend/ # Vue 3 frontend application
│ ├── src/
│ │ ├── App.vue # Main component with logic and UI
│ │ ├── style.css # Tailwind directives
│ │ └── main.ts
│ ├── index.html
│ ├── package.json
│ ├── tailwind.config.js
│ ├── postcss.config.js
│ └── vite.config.ts
├── .gitignore
└── README.md

## Configuration

No `.env` file or API keys are required. The application runs entirely locally using deterministic algorithms.

If deploying to production, ensure you update the `allow_origins` list in `backend/main.py` to include your deployed frontend URL.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.