from fastapi import FastAPI  # type: ignore
import logging
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
from functions import tweet_cleaning
import os

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

model = load_model("./lstm_model_keras.keras")

with open("tokenizer.pickle", "rb") as t:
    tokenizer = pickle.load(t)


app = FastAPI()


@app.get("/predict")
async def simple_prediction(sentence):
    """Fait une prediction sur une phrase

    Args:
        sentence (string): The sentence you want to predict the sentiment
    Returns:
        json: A json with the sentence and the prediction or the error message
    """

    try:
        clean_sentence = tweet_cleaning(sentence)
        sample_seq = tokenizer.texts_to_sequences([clean_sentence])
        sample_pad = pad_sequences(sample_seq, maxlen=10_000)

        pred = model.predict(sample_pad)

        if pred[0][0] > 0.5:
            return {"sentence": sentence, "sentiment": "Positif", 'score': pred}
        else:
            return {"sentence": sentence, "sentiment": "Negatif", 'score': pred}

    except Exception as error:
        logging.error("An Error occured during the prediction: ", error)
        return {"sentence": sentence, "error": "Consult logs"}
