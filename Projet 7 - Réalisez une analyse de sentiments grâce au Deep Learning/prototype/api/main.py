from fastapi import FastAPI, HTTPException
import logging
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
from functions import tweet_cleaning
import os

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Charger le modèle et le tokenizer
model = load_model("./lstm_model_keras.keras")
with open("tokenizer.pickle", "rb") as t:
    tokenizer = pickle.load(t)

app = FastAPI()

@app.get("/predict")
async def simple_prediction(sentence: str):
    """Fait une prédiction sur une phrase"""
    try:
        clean_sentence = tweet_cleaning(sentence)
        sample_seq = tokenizer.texts_to_sequences([clean_sentence])
        sample_pad = pad_sequences(sample_seq, maxlen=10_000)

        pred_value = float(model.predict(sample_pad)[0][0])

        if pred_value > 0.5:
            return {"sentence": sentence, "sentiment": "Positif", "score": round(pred_value, 2)}
        else:
            return {"sentence": sentence, "sentiment": "Negatif", "score": round(pred_value, 2)}

    except Exception as error:
        logging.error(f"Erreur lors de la prédiction : {error}")
        raise HTTPException(
            status_code=500,
            detail={"sentence": sentence, "error": "Consult logs"}
        )