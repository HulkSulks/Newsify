import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib
import os
import re

def clean_text_simple(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_data():
    print("Loading data from datasets/...")
    if not os.path.exists("datasets/Fake.csv") or not os.path.exists("datasets/True.csv"):
        print("Error: datasets/Fake.csv and datasets/True.csv not found.")
        print("Please download them from Kaggle and place them in the datasets/ directory.")
        return None
        
    fake_df = pd.read_csv("datasets/Fake.csv")
    true_df = pd.read_csv("datasets/True.csv")
    
    # Add labels: 0 for Fake, 1 for Real
    fake_df['label'] = 0
    true_df['label'] = 1
    
    df = pd.concat([fake_df, true_df], ignore_index=True)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print("Cleaning data...")
    df['text'] = df['text'].apply(clean_text_simple)
    return df

def vectorize_text(train_texts, test_texts):
    print("Vectorizing text (this might take a while)...")
    vectorizer = TfidfVectorizer(
        max_features=50000,
        stop_words="english",
        ngram_range=(1, 2)
    )
    X_train = vectorizer.fit_transform(train_texts)
    X_test = vectorizer.transform(test_texts)
    return vectorizer, X_train, X_test

def train_and_evaluate(X_train, X_test, y_train, y_test):
    print("Training Logistic Regression model...")
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    lr_predictions = lr_model.predict(X_test)
    lr_accuracy = accuracy_score(y_test, lr_predictions)
    print(f"Accuracy: {lr_accuracy * 100:.2f}%")
    return lr_model

def train():
    df = load_data()
    if df is None:
        return False
        
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(df['text'], df['label'], test_size=0.2, random_state=42)
    
    vectorizer, X_train, X_test = vectorize_text(X_train_raw, X_test_raw)
    model = train_and_evaluate(X_train, X_test, y_train, y_test)
    
    print("Saving model and vectorizer...")
    joblib.dump(model, "model.pkl")
    joblib.dump(vectorizer, "vectorizer.pkl")
    print("Done! Models saved as model.pkl and vectorizer.pkl.")
    return True

if __name__ == "__main__":
    train()
