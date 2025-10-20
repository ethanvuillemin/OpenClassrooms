# functions/popularity.py
import pandas as pd

def get_popular_recommendations(dataframe: pd.DataFrame, top_n: int = 5):
    """
    Génère des recommandations basées sur la popularité des articles.

    Args:
        dataframe (pd.DataFrame): Le DataFrame contenant les interactions utilisateur-article.
        top_n (int): Le nombre d'articles populaires à retourner.

    Returns:
        list: Une liste de dictionnaires contenant 'article_id' et 'popularity'.
    """
    # Calculer la popularité (nombre de clics) pour chaque article
    popular_articles = dataframe['click_article_id'].value_counts()
    # Sélectionner les top_n articles les plus populaires
    top_articles = popular_articles.head(top_n)
    # Formater les résultats
    recommendations = []
    for article_id, count in top_articles.items():
        recommendations.append({
            "article_id": article_id,
            "popularity": int(count) # Assurez-vous que c'est un entier
        })
    return recommendations
