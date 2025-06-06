from fastapi import FastAPI #type: ignore
import logging

app = FastAPI()


@app.get('/predict')
async def simple_prediction(sentence):
    """Fait une prediction sur une phrase

    Args:
        sentence (string): The sentence you want to predict the sentiment
    Returns:
        json: A json with the sentence and the prediction or the error message
    """

    try:
        print("some function")



    except Exception as error:
        logging.error('An Error occured during the prediction: ', error)


    return 'hello world !'