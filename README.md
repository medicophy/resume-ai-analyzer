# Resume AI Analyzer

Resume AI Analyzer is a modern web application that leverages artificial intelligence to help job seekers optimize their resumes for Applicant Tracking Systems (ATS) and hiring managers. It provides instant feedback on keyword matching, readability, and overall impact, ensuring your resume stands out in the competitive job market.

## Features

- **ATS Keyword Optimization**: Analyzes your resume against specific job descriptions to identify missing keywords and suggest improvements.
- **Readability Score**: Calculates the Flesch-Kincaid readability score to ensure your resume is easy to read and understand.
- **AI-Powered Feedback**: Uses advanced AI models to provide personalized suggestions for improving content, structure, and formatting.
- **Modern User Interface**: A clean, intuitive, and responsive interface built with React and Tailwind CSS.
- **Fast & Efficient**: Built on a robust backend with FastAPI and optimized for performance.

## Tech Stack

### Frontend
- **Framework**: React 18+
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query (React Query)
- **Build Tool**: Vite

### Backend
- **Framework**: FastAPI (Python)
- **AI/ML**: LangChain, OpenAI API
- **Database**: SQLite (for development), PostgreSQL (production)
- **Authentication**: JWT (JSON Web Tokens)
- **Deployment**: Docker, Docker Compose

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python (v3.8+)
- Docker (optional, for containerized deployment)

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
    source venv/bin/activate  # On Windows: venv\Scripts\activate
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
    uvicorn main:app --reload
    ```
    The API will be available at `http://localhost:8000`.

2.  **Start the Frontend**
    ```bash
    cd ../frontend
    npm run dev
    ```
    The application will be available at `http://localhost:5173`.

## Project Structure

```
resume-ai-analyzer/
├── backend/            # FastAPI backend application
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/           # React frontend application
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── .gitignore
├── README.md
└── docker-compose.yml  # Optional: For containerized deployment
```

## Configuration

Ensure you have an `.env` file in the `backend` directory with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./test.db
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.