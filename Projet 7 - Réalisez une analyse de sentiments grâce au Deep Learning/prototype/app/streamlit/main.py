import streamlit as st
import pandas as pd
import numpy as np
import random

df = pd.DataFrame(
        np.random.randn(50, 20), columns=("col %d" % i for i in range(20))
    )


@st.cache_data
def get_data():
    df = pd.DataFrame(
        np.random.randn(50, 20), columns=("col %d" % i for i in range(20))
    )
    return df

@st.cache_data
def convert_for_download(df):
    return df.to_csv().encode("utf-8")

df = get_data()
csv = convert_for_download(df)




def single_sentiment_analysis():
    return int(random.choice([0,1]))

def multi_sentiment_analysis():
    return "Soon ..."


st.title("Air paradis - Sentiment analysis prototype")
st.subheader('Put a dataframe or test with one sentence to see if its work')

col1, col2 = st.columns(2)


st.subheader("Unique input")

single_form = st.form('Input text')

single_text_input = single_form.text_input("Your sentence: ", "World's best airline !")
single_text_submit_button  = single_form.form_submit_button("Click to predict the sentiment")

if single_text_submit_button:
    sentiment = single_sentiment_analysis()
    print(sentiment)
    if sentiment == 0:
        single_form.text("its Positive !")
    else:
        single_form.text("its Negative !")


st.subheader("Multiple input")
multi_form = st.form("Csv file")

multi_form.file_uploader(label="Upload your csv file here", type="csv")
multi_text_submit_button  = multi_form.form_submit_button("Submit")


if multi_text_submit_button:
    sentiments = multi_sentiment_analysis()
    st.download_button(
    label="Download CSV",
    data=csv,
    file_name="data.csv",
    mime="text/csv",
    icon=":material/download:",
)


