import numpy as np
import pandas as pd
import requests
import streamlit as st
import io
from collections import Counter

# Fonction pour générer des données aléatoires
@st.cache_data
def get_data():
    df = pd.DataFrame(
        np.random.randn(50, 20), columns=("col %d" % i for i in range(20))
    )
    return df

# Fonction pour convertir les données en CSV pour téléchargement
@st.cache_data
def convert_for_download(df):
    return df.to_csv(index=False).encode("utf-8")

df = get_data()
csv = convert_for_download(df)

# Fonction pour l'analyse de sentiment d'une seule phrase
def single_sentiment_analysis(sentence):
    try:
        response = requests.get(f"http://cityhand.fr:8007/predict?sentence={sentence}")
        response.raise_for_status()
        res = response.json()
        print(res)
        # Normaliser le sentiment pour correspondre exactement à "Positif" ou "Negatif"
        sentiment = res.get("sentiment", "unknown").capitalize()
        if sentiment == "Positive":
            sentiment = "Positif"
        elif sentiment == "Negative":
            sentiment = "Negatif"
        return sentiment, res.get("score", 0)
    except Exception as e:
        print(f"Error analyzing sentence: {e}")
        return "unknown", 0

# Fonction pour l'analyse de sentiment multiple
def multi_sentiment_analysis(uploaded_file):
    # Lire le fichier CSV
    df = pd.read_csv(uploaded_file)

    # Vérifier si le DataFrame a une colonne nommée 'sentence'
    if 'sentence' not in df.columns:
        st.error("Le fichier CSV doit contenir une colonne nommée 'sentence'.")
        return None, None, None, None

    # Appliquer l'analyse de sentiment à chaque phrase
    results = df['sentence'].apply(single_sentiment_analysis)
    df['sentiment'] = results.apply(lambda x: x[0])
    df['score'] = results.apply(lambda x: x[1])

    # Compter spécifiquement les valeurs "Positif" et "Negatif"
    sentiment_counts = Counter(df['sentiment'])
    total_sentences = len(df)
    positif_count = sentiment_counts.get('Positif', 0)
    negatif_count = sentiment_counts.get('Negatif', 0)

    # Convertir le DataFrame en CSV pour téléchargement
    csv_output = convert_for_download(df)

    return csv_output, total_sentences, positif_count, negatif_count

# Titre et sous-titre de l'application
st.title("Air paradis - Sentiment analysis prototype")
st.subheader("Put a dataframe or test with one sentence to see if it works")

# Section pour l'analyse de sentiment unique
st.subheader("Unique input")

single_form = st.form("Input text")

single_text_input = single_form.text_input("Your sentence:", "it is too bad i would not recommend")
single_text_submit_button = single_form.form_submit_button("Click to predict the sentiment")

if single_text_submit_button:
    sentiment, score = single_sentiment_analysis(single_text_input)
    st.write(f"Sentiment: {sentiment}")
    st.write(f"Score: {score}")

# Section pour l'analyse de sentiment multiple
st.subheader("Multiple input")
multi_form = st.form("Csv file")

uploaded_file = multi_form.file_uploader(label="Upload your CSV file here", type="csv")
multi_text_submit_button = multi_form.form_submit_button("Submit")

if multi_text_submit_button and uploaded_file is not None:
    with st.spinner('Analyse en cours...'):
        csv_output, total, positif, negatif = multi_sentiment_analysis(uploaded_file)
        if csv_output is not None:
            # Affichage des statistiques
            st.markdown(
                f"""
                <div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; border-left: 5px solid #4e79a7; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
                    <h3 style="margin-top: 0; color: #f0f2f6;">Résultats de l'analyse</h3>
                    <p style="color: #f0f2f6;"><strong>Nombre total de phrases analysées:</strong> {total}</p>
                    <p style="color: #f0f2f6;"><strong style="color: #2ecc71;">Phrases Positif:</strong> {positif}</p>
                    <p style="color: #f0f2f6;"><strong style="color: #e74c3c;">Phrases Negatif:</strong> {negatif}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.download_button(
                label="Télécharger le CSV avec prédictions",
                data=csv_output,
                file_name="data_with_sentiments_and_scores.csv",
                mime="text/csv",
            )
