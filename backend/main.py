from fastapi import FastAPI, UploadFile, File, HTTPException, Form 
from fastapi.middleware.cors import CORSMiddleware
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import fitz  # This is PyMuPDF
import io
import re
import string
from collections import Counter

# Initialize App
app = FastAPI(title="Resume AI Analyzer")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_keywords(text: str, top_n: int = 15) -> list:
    words = clean_text(text).split()
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'it', 'this', 'that'}
    filtered_words = [w for w in words if len(w) > 3 and w not in stop_words]
    counts = Counter(filtered_words)
    return [word for word, count in counts.most_common(top_n)]

@app.get("/")
async def root():
    return {"status": "online", "message": "Resume AI Analyzer Backend Ready"}

@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...), 
    job_description: str = Form("")  # <--- CHANGED: Explicitly declare as Form
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    try:
        # 1. Extract Text using PyMuPDF (fitz)
        resume_text = ""
        file_bytes = await file.read()
        
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text = page.get_text()
            if text:
                resume_text += text + "\n"
        doc.close()

        # DEBUG Logging
        print(f"--- DEBUG ---")
        print(f"File: {file.filename}")
        print(f"Extracted Length: {len(resume_text)}")
        print(f"JD Received Length: {len(job_description)}") # <--- Check this
        if len(job_description) > 0:
            print(f"JD Preview: {job_description[:50]}...")
        print(f"-------------")

        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text. The PDF might be an image scan.")

        if not job_description.strip():
             # If it's still empty here, the Form fix didn't work, but let's try anyway
             print("WARNING: Job description is empty despite Form definition.")
             # We will allow it to proceed but score will be 0, or return error
             # Let's return a specific error to be sure
             raise HTTPException(status_code=400, detail="Job description received empty. Check Frontend FormData.")

        # 2. Clean Data
        clean_resume = clean_text(resume_text)
        clean_jd = clean_text(job_description)

        # 3. Calculate Match Score
        tfidf = TfidfVectorizer(stop_words='english')
        try:
            tfidf_matrix = tfidf.fit_transform([clean_resume, clean_jd])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            match_score = round(similarity * 100, 2)
        except ValueError:
            match_score = 0.0

        # 4. Find Missing Keywords
        jd_keywords = set(extract_keywords(job_description, top_n=20))
        resume_keywords = set(extract_keywords(resume_text, top_n=50))
        missing_keywords = list(jd_keywords - resume_keywords)

        return {
            "filename": file.filename,
            "char_count": len(resume_text),
            "match_score": match_score,
            "missing_keywords": missing_keywords[:10],
            "resume_preview": resume_text[:150] + "..."
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)