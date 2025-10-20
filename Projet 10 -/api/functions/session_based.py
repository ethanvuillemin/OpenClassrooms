# functions/session_based.py
import pandas as pd

def load_and_prepare_session_data(dataframe: pd.DataFrame):
    """
    Prépare les données à partir d'un DataFrame pour le filtrage basé sur les sessions.

    Args:
        dataframe (pd.DataFrame): Le DataFrame contenant les interactions utilisateur-article.

    Returns:
        pd.DataFrame: Le DataFrame chargé et nettoyé.
    """
    # Assurez-vous que le DataFrame est nettoyé
    df_clean = dataframe.dropna(subset=['click_article_id'])
    # Assurez-vous que 'click_timestamp' est triable (datetime si possible, sinon string)
    # Ici, on suppose qu'il est déjà triable
    return df_clean

def get_session_based_recommendations(user_id: str, dataframe: pd.DataFrame, top_n: int = 5):
    """
    Génère des recommandations basées sur la session d'un utilisateur.

    Args:
        user_id (str): L'ID de l'utilisateur (sous forme de chaîne).
        dataframe (pd.DataFrame): Le DataFrame contenant les interactions.
        top_n (int): Le nombre de recommandations à retourner.

    Returns:
        list: Une liste de dictionnaires contenant 'article_id' et 'popularity'.
    """
    # Convertir user_id en int si les IDs dans le df sont des entiers
    try:
        user_id_int = int(user_id)
    except ValueError:
        # Si la conversion échoue, l'ID n'est pas valide
        return []

    df_clean = load_and_prepare_session_data(dataframe) # On utilise la fonction pour nettoyer
    user_clicks = df_clean[df_clean['user_id'] == user_id_int]
    if user_clicks.empty:
        # Si l'utilisateur est inconnu, retourner les articles populaires
        popular_articles = dataframe['click_article_id'].value_counts()
        top_articles = popular_articles.head(top_n)
        recommendations = [{"article_id": int(art_id), "popularity": int(count)} for art_id, count in top_articles.items()]
        return recommendations

    # Exemple simplifié : recommander les articles les plus récents de la session utilisateur
    recent_articles_df = user_clicks.sort_values('click_timestamp', ascending=False).head(top_n*2)
    unique_recent_article_ids = recent_articles_df['click_article_id'].drop_duplicates().head(top_n).tolist()

    # Calculer la popularité pour les articles de la session en utilisant le dataframe original
    popularity_counts = dataframe['click_article_id'].value_counts()
    recommendations = []
    for article_id in unique_recent_article_ids:
        pop_count = int(popularity_counts.get(article_id, 0))
        recommendations.append({
            "article_id": int(article_id), # Assurez-vous que c'est un entier
            "popularity": pop_count
        })

    return recommendations
