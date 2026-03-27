import pandas as pd
import numpy as np
import pickle
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import os

# Ensure NLTK resources are downloaded
try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except Exception as e:
    print(f"NLTK Download Error: {e}")

# Define synthetic datasets to bootstrap the app without needing massive CSV downloads
print("Generating synthetic datasets...")

fake_news_data = [
    # Fake News (1)
    ("The earth is flat and scientists are hiding the truth from you.", 1),
    ("Alien spaceship found in Antarctica with ancient technology.", 1),
    ("Miracle cure discovered! Drink this tea to cure all diseases instantly.", 1),
    ("Politician spotted transforming into a lizard person.", 1),
    ("Secret shadow government controls all weather using 5G towers.", 1),
    ("Drinking bleach will make you immune to all viruses.", 1),
    ("Giant 50-foot snake found in the Amazon river eating boats.", 1),
    ("Local man has not slept for 10 years, doctors are baffled.", 1),
    # Real News (0)
    ("The stock market experienced a slight decline today due to inflation fears.", 0),
    ("NASA successfully launched a new satellite to study climate change.", 0),
    ("Vaccines have been proven effective in reducing the spread of diseases.", 0),
    ("Local authorities urge citizens to prepare for the upcoming storm.", 0),
    ("The new tech conference starts tomorrow in San Francisco.", 0),
    ("Federal Reserve announces interest rate hike to combat rising prices.", 0),
    ("A new species of frog was discovered in the rainforest by researchers.", 0),
    ("Election results indicate a close race between the two leading candidates.", 0)
]

phishing_data = [
    # Phishing (1)
    ("URGENT: Your bank account has been locked. Click here to verify your identity.", 1),
    ("Congratulations! You've won a $1000 Walmart gift card. Claim it now!", 1),
    ("Your PayPal account is restricted. Update your billing information immediately.", 1),
    ("Important Notice: Your email password has expired. Please reset it here.", 1),
    ("You have a package pending delivery. Pay the $2.99 shipping fee at this link.", 1),
    ("Netflix: Your payment was declined. Update your credit card details.", 1),
    ("Dear customer, please find the attached invoice for your recent purchase of $900.", 1),
    ("Attention: Hackers have accessed your computer. Call this number immediately.", 1),
    # Legitimate (0)
    ("Hi John, just following up on our meeting tomorrow at 10 AM.", 0),
    ("Your Amazon order #12345 has been shipped and will arrive by Friday.", 0),
    ("Newsletter: Top 10 programming languages to learn this year.", 0),
    ("Reminder: Doctor appointment scheduled for next Tuesday at 2 PM.", 0),
    ("Your GitHub push was successful. Build passed.", 0),
    ("Hey mom, I'll be home late tonight. Can you save me some dinner?", 0),
    ("Meeting notes from today's brainstorming session attached.", 0),
    ("Your monthly subscription receipt from Spotify.", 0)
]

print("Preprocessing and Training Fake News Model...")
df_news = pd.DataFrame(fake_news_data, columns=['text', 'label'])
vectorizer_news = TfidfVectorizer(max_features=5000, stop_words='english')
X_news = vectorizer_news.fit_transform(df_news['text'])
y_news = df_news['label']

model_news = LogisticRegression()
model_news.fit(X_news, y_news)

print("Preprocessing and Training Phishing Model...")
df_phishing = pd.DataFrame(phishing_data, columns=['text', 'label'])
# We will use the same vectorizer approach but fit it on the respective dataset
vectorizer_phish = TfidfVectorizer(max_features=5000, stop_words='english')
X_phish = vectorizer_phish.fit_transform(df_phishing['text'])
y_phish = df_phishing['label']

model_phishing = MultinomialNB()
model_phishing.fit(X_phish, y_phish)

print("Saving models...")
os.makedirs('models', exist_ok=True)
with open('models/fake_news_model.pkl', 'wb') as f:
    pickle.dump(model_news, f)
    
with open('models/fake_news_vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer_news, f)

with open('models/phishing_model.pkl', 'wb') as f:
    pickle.dump(model_phishing, f)

with open('models/phishing_vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer_phish, f)

print("Training complete! Models saved in the 'models' directory.")
