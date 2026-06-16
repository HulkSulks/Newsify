import os
import joblib
from utils import clean_text

MODEL_PATH = "model.pkl"
VECTORIZER_PATH = "vectorizer.pkl"

loaded_model = None
loaded_vectorizer = None

def load_models():
    global loaded_model, loaded_vectorizer
    if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
        loaded_model = joblib.load(MODEL_PATH)
        loaded_vectorizer = joblib.load(VECTORIZER_PATH)
        return True
    return False

def generate_explanation(label, confidence, text):
    if label == "REAL":
        if confidence > 0.8:
            return "The model is highly confident this is REAL news based on the linguistic patterns found in reputable journalism."
        else:
            return "The model leans towards this being REAL news, but with some uncertainty."
    else:
        if confidence > 0.8:
            return "The model is highly confident this is FAKE news due to sensationalist or uncharacteristic language patterns."
        else:
            return "The model suspects this might be FAKE news, but suggests further fact-checking."

def predict_news(text):
    if loaded_model is None or loaded_vectorizer is None:
        if not load_models():
            raise Exception("Models not found. Please train the model first.")
            
    cleaned = clean_text(text)
    if not cleaned:
        raise ValueError("No valid text found to analyze.")
        
    # Convert text into TF-IDF features
    text_features = loaded_vectorizer.transform([cleaned])

    # Get prediction and probabilities
    prediction = loaded_model.predict(text_features)[0]
    probabilities = loaded_model.predict_proba(text_features)[0]
    
    classes = loaded_model.classes_
    fake_idx = list(classes).index(0)
    real_idx = list(classes).index(1)
    
    fake_prob = probabilities[fake_idx]
    real_prob = probabilities[real_idx]
    
    confidence = max(fake_prob, real_prob)
    label = "REAL" if prediction == 1 else "FAKE"

    return {
        "label": label,
        "real_prob": real_prob,
        "fake_prob": fake_prob,
        "confidence": confidence,
        "explanation": generate_explanation(label, confidence, cleaned)
    }
