# ============================================================
# STEP 5A: FastAPI BACKEND  (api/main.py)
# ============================================================
# HOW TO RUN LOCALLY:
#   pip install fastapi uvicorn transformers torch
#   uvicorn api.main:app --reload
#   Then open: http://localhost:8000/docs  ← interactive test UI!

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import os

# ─── App setup ───────────────────────────────────────────────
app = FastAPI(
    title="TruthLens API",
    description="Fake News Detection powered by fine-tuned RoBERTa",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # allow Streamlit to call this
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Load model at startup ───────────────────────────────────
MODEL_PATH = os.getenv("MODEL_PATH", "./saved_model")

print(f"Loading model from {MODEL_PATH}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model     = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
print(f"✅ Model loaded on {device}")

# ─── Request/Response schemas ────────────────────────────────
class PredictRequest(BaseModel):
    text: str

    class Config:
        schema_extra = {
            "example": {
                "text": "Scientists discover miracle cure hidden by Big Pharma!"
            }
        }

class PredictResponse(BaseModel):
    label:       str          # "FAKE" or "REAL"
    confidence:  float        # 0.0 to 100.0
    fake_prob:   float
    real_prob:   float
    risk_score:  int          # 0-100
    signals:     list[dict]

# ─── Prediction function ─────────────────────────────────────
def predict(text: str) -> dict:
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=128,
        padding=True
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        probs   = torch.softmax(outputs.logits, dim=1).cpu().numpy()[0]

    fake_prob = float(probs[0])
    real_prob = float(probs[1])
    label     = "FAKE" if fake_prob > real_prob else "REAL"
    confidence = max(fake_prob, real_prob) * 100
    risk_score = int(fake_prob * 100)

    # Rule-based signals (additional layer)
    signals = _compute_signals(text)

    return {
        "label":      label,
        "confidence": round(confidence, 1),
        "fake_prob":  round(fake_prob * 100, 1),
        "real_prob":  round(real_prob * 100, 1),
        "risk_score": risk_score,
        "signals":    signals
    }

def _compute_signals(text: str) -> list:
    """Heuristic signal analysis on top of the model."""
    lower   = text.lower()
    signals = []

    # Capitalization check
    cap_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    signals.append({
        "name":  "Excessive Capitalization",
        "value": f"{cap_ratio*100:.0f}%",
        "risk":  "HIGH" if cap_ratio > 0.2 else "LOW"
    })

    # Exclamation marks
    excl = text.count('!')
    signals.append({
        "name":  "Exclamation Marks",
        "value": str(excl),
        "risk":  "HIGH" if excl >= 3 else ("MEDIUM" if excl >= 1 else "LOW")
    })

    # Sensational words
    sens_words = ['shocking','breaking','bombshell','secret','hidden',
                  'suppressed','miracle','exposed','wake up','they don\'t want']
    found = [w for w in sens_words if w in lower]
    signals.append({
        "name":  "Sensational Language",
        "value": ", ".join(found) if found else "none",
        "risk":  "HIGH" if len(found) >= 2 else ("MEDIUM" if found else "LOW")
    })

    # Source indicators
    factual_words = ['according to','study','research','published','reported','announced']
    factual = [w for w in factual_words if w in lower]
    signals.append({
        "name":  "Factual Language",
        "value": f"{len(factual)} indicators",
        "risk":  "LOW" if len(factual) >= 2 else "HIGH"
    })

    return signals

# ─── Routes ──────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "TruthLens API is running!", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok", "model": "roberta-base-finetuned", "device": str(device)}

@app.post("/predict", response_model=PredictResponse)
def predict_endpoint(req: PredictRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    if len(req.text) > 5000:
        raise HTTPException(status_code=400, detail="Text too long (max 5000 chars)")

    return predict(req.text)

@app.get("/docs-info")
def docs_info():
    return {
        "endpoints": [
            "GET  /          → health check",
            "GET  /health    → model status",
            "POST /predict   → main prediction endpoint"
        ],
        "example_request": {
            "text": "Your news article here..."
        }
    }
