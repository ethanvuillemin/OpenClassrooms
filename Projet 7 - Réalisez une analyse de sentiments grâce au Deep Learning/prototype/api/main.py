from fastapi import FastAPI, HTTPException
import logging
import time
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
from functions import tweet_cleaning
import os
from dotenv import load_dotenv
from applicationinsights import TelemetryClient

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Désactiver warning TF
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Charger le modèle et le tokenizer
model = load_model("./lstm_model_keras.keras")
with open("tokenizer.pickle", "rb") as t:
    tokenizer = pickle.load(t)

# Initialiser FastAPI
app = FastAPI()

# Récupérer la clé d'instrumentation
INSTRUMENTATION_KEY = os.getenv("APPINSIGHTS_INSTRUMENTATIONKEY")

if INSTRUMENTATION_KEY:
    logger.info("Clé d'instrumentation trouvée. Connexion à Azure Application Insights en cours...")
    tc = TelemetryClient(INSTRUMENTATION_KEY)
    logger.info("Connexion à Azure Application Insights réussie.")
else:
    logger.error("Aucune clé d'instrumentation trouvée. Les données ne seront pas envoyées à Azure.")
    tc = None  # Pour éviter les erreurs si la clé n'est pas présente

@app.get("/predict")
async def simple_prediction(sentence: str):
    """Fait une prédiction sur une phrase"""
    
    start_time = time.time()
    logger.info(f"Début de la prédiction pour la phrase : {sentence}")

    try:
        # Nettoyage du texte
        clean_sentence = tweet_cleaning(sentence)
        logger.debug(f"Phrase nettoyée : {clean_sentence}")

        # Tokenisation
        sample_seq = tokenizer.texts_to_sequences([clean_sentence])
        logger.debug(f"Séquence tokenisée : {sample_seq}")

        # Padding
        sample_pad = pad_sequences(sample_seq, maxlen=10_000)
        logger.debug(f"Padding appliqué, shape : {sample_pad.shape}")

        # Prédiction
        pred_value = float(model.predict(sample_pad)[0][0])
        elapsed = time.time() - start_time
        logger.info(f"Prédiction calculée : {pred_value} en {elapsed:.2f}s")

        # Déterminer le sentiment
        sentiment = "Positif" if pred_value > 0.5 else "Negatif"
        result = {"sentence": sentence, "sentiment": sentiment, "score": round(pred_value, 2)}

        # Enregistrer l'événement dans Application Insights si la connexion est active
        if tc:
            event_data = {
                'sentiment': sentiment,
                'score': str(round(pred_value, 2)),
                'sentence': sentence[:100],
                'processing_time': str(elapsed),
            }
            tc.track_event('Prediction', event_data)
            logger.info("Données envoyées à Azure Application Insights.")

        return result

    except Exception as error:
        logger.error(f"Erreur lors de la prédiction : {error}", exc_info=True)
        if tc:
            tc.track_exception()
            logger.info("Exception envoyée à Azure Application Insights.")
        raise HTTPException(
            status_code=500,
            detail={"sentence": sentence, "error": "Consult logs"}
        )

@app.on_event("shutdown")
def shutdown_event():
    """Assure que toutes les données soient envoyées avant l'arrêt"""
    logger.info("Arrêt de l'application. Envoi final des données à Azure.")
    if tc:
        tc.flush()