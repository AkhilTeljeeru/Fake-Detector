from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

app = FastAPI(title="Fake News & Phishing Detection API")

# Setup CORS
FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://fake-detector-sigma.vercel.app")
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    FRONTEND_URL,
    "https://fake-detector-sigma.vercel.app" # hardcoded fallback
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://fake-detector-.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input Models
class NewsInput(BaseModel):
    text: str

class EmailInput(BaseModel):
    text: str

class SearchInput(BaseModel):
    query: str

class UrlInput(BaseModel):
    url: str

# Load ML Models
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

model_news = None
vectorizer_news = None
model_phishing = None
vectorizer_phishing = None

@app.on_event("startup")
def load_models():
    global model_news, vectorizer_news, model_phishing, vectorizer_phishing
    try:
        with open(os.path.join(MODEL_DIR, "fake_news_model.pkl"), "rb") as f:
            model_news = pickle.load(f)
        with open(os.path.join(MODEL_DIR, "fake_news_vectorizer.pkl"), "rb") as f:
            vectorizer_news = pickle.load(f)
            
        with open(os.path.join(MODEL_DIR, "phishing_model.pkl"), "rb") as f:
            model_phishing = pickle.load(f)
        with open(os.path.join(MODEL_DIR, "phishing_vectorizer.pkl"), "rb") as f:
            vectorizer_phishing = pickle.load(f)
            
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Error loading models: {e}. Make sure to run train.py first!")

@app.get("/")
def read_root():
    return {"message": "Welcome to Fake News & Phishing Detection API"}

@app.post("/predict-news")
def predict_news(input_data: NewsInput):
    if not input_data.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    
    if model_news is None or vectorizer_news is None:
        raise HTTPException(status_code=500, detail="Models are not loaded.")

    try:
        text_vectorized = vectorizer_news.transform([input_data.text])
        prediction = model_news.predict(text_vectorized)[0]
        # predict_proba returns array of shape (1, n_classes), we get the max prob
        proba = model_news.predict_proba(text_vectorized)[0]
        confidence = float(max(proba))
        
        # 1: Fake, 0: Real
        label = "Fake News" if prediction == 1 else "Real News"
        
        return {
            "prediction": label,
            "confidence": round(confidence, 4)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict-phishing")
def predict_phishing(input_data: EmailInput):
    if not input_data.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
        
    if model_phishing is None or vectorizer_phishing is None:
        raise HTTPException(status_code=500, detail="Models are not loaded.")

    try:
        text_vectorized = vectorizer_phishing.transform([input_data.text])
        prediction = model_phishing.predict(text_vectorized)[0]
        proba = model_phishing.predict_proba(text_vectorized)[0]
        confidence = float(max(proba))
        
        # 1: Phishing, 0: Legitimate
        label = "Phishing" if prediction == 1 else "Legitimate"
        
        return {
            "prediction": label,
            "confidence": round(confidence, 4)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-web")
def search_web(input_data: SearchInput):
    if not input_data.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")
        
    try:
        with DDGS() as ddgs:
            # Use ddgs.news to fetch article links (handles DDG's lenient anti-bot measures)
            results = list(ddgs.news(input_data.query, max_results=5))
        
        if not results:
             # DuckDuckGo rate limiting or empty
             raise HTTPException(status_code=429, detail="Search engine rate limit exceeded or no results found. Please try again in a few minutes or use the 'Manual Text' tab!")
             
        # duckduckgo-search .news() returns slightly different keys (e.g. 'title', 'url', 'source')
        # Map them back to what the frontend expects (href, body, title)
        formatted_results = []
        for r in results:
            formatted_results.append({
                "title": r.get('title', ''),
                "href": r.get('url', r.get('href', '')), 
                "body": f"Source: {r.get('source', 'News')} | {r.get('body', '')}" if r.get('source') else r.get('body', '')
            })
            
        return {"results": formatted_results}
    except Exception as e:
        if "rate limit" in str(e).lower() or isinstance(e, HTTPException):
             raise HTTPException(status_code=429, detail="Search engine rate limit exceeded. You typed too many searches too quickly! Please try again in 5 minutes.")
        raise HTTPException(status_code=500, detail=f"Error performing search: {str(e)}. Try using manual text instead!")

@app.post("/analyze-url")
def analyze_url(input_data: UrlInput):
    if not input_data.url.strip():
        raise HTTPException(status_code=400, detail="URL cannot be empty.")
        
    try:
        # Scrape the URL
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(input_data.url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text() for p in paragraphs])
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract any meaningful text from the URL.")
            
        # Re-use predict logic for news
        if model_news is None or vectorizer_news is None:
            raise HTTPException(status_code=500, detail="Models are not loaded.")
            
        text_vectorized = vectorizer_news.transform([text])
        prediction = model_news.predict(text_vectorized)[0]
        proba = model_news.predict_proba(text_vectorized)[0]
        confidence = float(max(proba))
        label = "Fake News" if prediction == 1 else "Real News"
        
        return {
            "prediction": label,
            "confidence": round(confidence, 4),
            "extracted_text": text[:300] + "..." if len(text) > 300 else text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze URL: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
