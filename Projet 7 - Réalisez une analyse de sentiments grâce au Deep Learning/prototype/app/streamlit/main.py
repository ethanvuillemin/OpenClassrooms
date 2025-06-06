import streamlit as st
import pandas as pd
import numpy as np
import random
import requests

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
    return df.to_csv().encode("utf-8")

df = get_data()
csv = convert_for_download(df)

# Fonction pour l'analyse de sentiment d'une seule phrase
def single_sentiment_analysis(sentence):
    response = requests.get(f'http://localhost:8000/predict?sentence={sentence}')
    res = response.json() 
    return  res['sentiment']

# Fonction pour l'analyse de sentiment multiple (à implémenter)
def multi_sentiment_analysis():
    return "Soon ..."

# Titre et sous-titre de l'application
st.title("Air paradis - Sentiment analysis prototype")
st.subheader('Put a dataframe or test with one sentence to see if it works')

# Section pour l'analyse de sentiment unique
st.subheader("Unique input")

single_form = st.form('Input text')

single_text_input = single_form.text_input("Your sentence:", "World's best airline!")
single_text_submit_button = single_form.form_submit_button("Click to predict the sentiment")

if single_text_submit_button:
    sentiment = single_sentiment_analysis(single_text_input)
    if sentiment == 0:
        st.write("It's Positive!")
    else:
        st.write("It's Negative!")

# Section pour l'analyse de sentiment multiple
st.subheader("Multiple input")
multi_form = st.form("Csv file")

uploaded_file = multi_form.file_uploader(label="Upload your CSV file here", type="csv")
multi_text_submit_button = multi_form.form_submit_button("Submit")

if multi_text_submit_button and uploaded_file is not None:
    sentiments = multi_sentiment_analysis()
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="data.csv",
        mime="text/csv",
        icon=":material/download:"
    )
