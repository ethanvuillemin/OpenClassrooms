# functions/item_based.py
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

def load_and_prepare_data(dataframe: pd.DataFrame):
    """
    Prépare les données à partir d'un DataFrame pour le filtrage collaboratif basé sur les items.

    Args:
        dataframe (pd.DataFrame): Le DataFrame contenant les interactions utilisateur-article.

    Returns:
        tuple: Un tuple contenant le DataFrame original et la matrice d'interaction binaire.
    """
    # Assurez-vous que le DataFrame est nettoyé
    df_clean = dataframe.dropna(subset=['click_article_id'])

    interaction_matrix = df_clean.pivot_table(
        index='user_id',
        columns='click_article_id',
        values='click_timestamp',
        aggfunc='count',
        fill_value=0
    )
    interaction_matrix_binary = interaction_matrix.astype(bool).astype(int)
    return df_clean, interaction_matrix_binary

def get_item_based_collaborative_recommendations(user_id: int, dataframe: pd.DataFrame, interaction_matrix: pd.DataFrame, top_n: int = 5):
    """
    Génère des recommandations basées sur les items pour un utilisateur donné.

    Args:
        user_id (int): L'ID de l'utilisateur.
        dataframe (pd.DataFrame): Le DataFrame original pour calculer la popularité.
        interaction_matrix (pd.DataFrame): La matrice d'interaction utilisateur-article.
        top_n (int): Le nombre de recommandations à retourner.

    Returns:
        list: Une liste de dictionnaires contenant 'article_id' et 'popularity'.
    """
    if user_id not in interaction_matrix.index:
        # Si l'utilisateur est inconnu, retourner les articles populaires
        popular_articles = dataframe['click_article_id'].value_counts()
        top_articles = popular_articles.head(top_n)
        recommendations = [{"article_id": int(art_id), "popularity": int(count)} for art_id, count in top_articles.items()]
        return recommendations

    user_interactions = interaction_matrix.loc[user_id]
    user_clicked_articles = user_interactions[user_interactions > 0].index.tolist()
    if not user_clicked_articles:
        # Si l'utilisateur n'a rien cliqué, retourner les articles populaires
        popular_articles = dataframe['click_article_id'].value_counts()
        top_articles = popular_articles.head(top_n)
        recommendations = [{"article_id": int(art_id), "popularity": int(count)} for art_id, count in top_articles.items()]
        return recommendations

    articles_matrix = interaction_matrix.T
    similarity_matrix = cosine_similarity(articles_matrix)
    similarity_df = pd.DataFrame(
        similarity_matrix,
        index=interaction_matrix.columns,
        columns=interaction_matrix.columns
    )
    scores = defaultdict(float)
    for article_consulte in user_clicked_articles:
        similarities_to_article = similarity_df[article_consulte]
        for other_article_id in interaction_matrix.columns:
            if other_article_id != article_consulte and other_article_id not in user_clicked_articles:
                scores[other_article_id] += similarities_to_article[other_article_id]

    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    recommended_article_ids = [article_id for article_id, score in sorted_scores[:top_n]]

    # Calculer la popularité pour les articles recommandés en utilisant le dataframe original
    popularity_counts = dataframe['click_article_id'].value_counts()
    recommendations = []
    for article_id in recommended_article_ids:
        pop_count = int(popularity_counts.get(article_id, 0))
        recommendations.append({
            "article_id": int(article_id), # Assurez-vous que c'est un entier
            "popularity": pop_count
        })

    return recommendations
