#  AI Fake News & Phishing Detection System

A complete FULL-STACK AI Web Application to classify text into:
1. Fake News vs. Real News
2. Phishing Emails vs. Legitimate Emails

This system features a dark-themed React UI and a fast, scalable FastAPI backend powered by Scikit-Learn NLP models.

##  Features
- **Frontend**: React.js with a modern dark theme and dynamic status coloring.
- **Backend API**: FastAPI with CORS enabled for seamless frontend-backend communication.
- **Machine Learning**: 
  - Fake News Detection (Logistic Regression)
  - Phishing Email Detection (Multinomial Naive Bayes)
  - TF-IDF Vectorization
- **Security Check**: Input validation to prevent empty queries.
- **Confidence Scores**: Displays AI confidence percentage alongside predictions.

## 🛠️ Tech Stack
- **Frontend**: React.js, Vite, Vanilla CSS
- **Backend**: FastAPI, Uvicorn, Python
- **Machine Learning**: Scikit-Learn, Pandas, NLTK
- **Storage**: Pickled models and vectorizers

## Setup Instructions

### 1. Backend Setup
Navigate to the backend folder, create a virtual environment, and install dependencies.
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Train the Models
Train the NLP models on synthetic datasets to run the app immediately.
```bash
python train.py
```
This will generate `fake_news_model.pkl`, `phishing_model.pkl`, and vectorizers in the `backend/models` directory.

### 3. Frontend Setup
Navigate to the frontend folder and install dependencies via npm.
```bash
cd frontend
npm install
```

## Run Instructions

### Start Backend API
From the `backend` folder with your virtual environment activated:
```bash
uvicorn app:app --reload
```
The FastAPI backend will bound to `http://localhost:8000`. API docs available at `http://localhost:8000/docs`.

### Start Frontend Dev Server
From the `frontend` folder:
```bash
npm run dev
```
Open the provided local URL (e.g., `http://localhost:5173`) in your browser to view the app!

## Test Cases
### Fake News Sample
> "Alien spaceship found in Antarctica with ancient technology." -> **Fake News**

### Real News Sample
> "NASA successfully launched a new satellite to study climate change." -> **Real News**

### Phishing Email Sample
> "URGENT: Your bank account has been locked. Click here to verify your identity." -> **Phishing**

### Legitimate Email Sample
> "Hi John, just following up on our meeting tomorrow at 10 AM." -> **Legitimate**

## API Documentation
- `POST /predict-news`
  - Body: `{ "text": "news content" }`
  - Returns: `{ "prediction": "Fake News", "confidence": 0.9854 }`
- `POST /predict-phishing`
  - Body: `{ "text": "email content" }`
  - Returns: `{ "prediction": "Phishing", "confidence": 0.9201 }`

