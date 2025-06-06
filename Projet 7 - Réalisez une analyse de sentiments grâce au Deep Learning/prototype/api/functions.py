import re
import string

def tweet_cleaning(tweet):
    """
    Nettoie et prétraite un tweet

    Cette fonction effectue plusieurs étapes de nettoyage :
        - Suppression des URLs, mentions et hashtags
        - Suppression des emojis et caractères spéciaux
        - Suppression de la ponctuation et des chiffres
        - Normalisation du texte (minuscules, espaces multiples)

    Params :
        tweet (str) : Le tweet brut à nettoyer.

    Return :
        str : Le tweet nettoyé et prétraité, prêt pour l'analyse de sentiment.

    """
    # Supprimer les URLs
    tweet = re.sub(r"https?://\S+|www\.\S+", "", tweet)

    # Supprimer les mentions (@user)
    tweet = re.sub(r"@\w+", "", tweet)

    # Supprimer les hashtags (#hashtag)
    tweet = re.sub(r"#\w+", "", tweet)

    # Normaliser & supprimer les caractères
    tweet = tweet.encode("ascii", "ignore").decode("utf-8")
    tweet = re.sub(r"[^\x00-\x7F]+", "", tweet)

    # Supprimer la ponctuation
    tweet = tweet.translate(str.maketrans("", "", string.punctuation))

    # Supprimer les chiffres
    tweet = re.sub(r"\d+", "", tweet)

    # Supprimer les espaces multiples et les espaces au début/fin
    tweet = re.sub(r"\s+", " ", tweet).strip()

    return tweet
