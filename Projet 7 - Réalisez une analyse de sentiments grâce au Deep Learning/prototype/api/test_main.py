import pytest
import numpy as np
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

@pytest.fixture
def mock_model_predict():
    with patch("main.model.predict") as mock:
        yield mock

@pytest.fixture
def mock_tweet_cleaning():
    with patch("functions.tweet_cleaning") as mock:
        yield mock


def test_predict_positive_sentiment(mock_model_predict, mock_tweet_cleaning):
    # Arrange
    sentence = "I love this product"
    cleaned_sentence = "love product"
    mock_tweet_cleaning.return_value = cleaned_sentence
    mock_model_predict.return_value = np.array([[0.9]], dtype=np.float32)

    # Act
    response = client.get(f"/predict?sentence={sentence}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["sentence"] == sentence
    assert data["sentiment"] in ["Positif", "Negatif"]
    assert 0 <= data["score"] <= 1


def test_predict_negative_sentiment(mock_model_predict, mock_tweet_cleaning):
    # Arrange
    sentence = "I hate this product"
    cleaned_sentence = "hate product"
    mock_tweet_cleaning.return_value = cleaned_sentence
    mock_model_predict.return_value = np.array([[0.4]], dtype=np.float32)

    # Act
    response = client.get(f"/predict?sentence={sentence}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["sentence"] == sentence
    assert data["sentiment"] in ["Positif", "Negatif"]
    assert 0 <= data["score"] <= 1

