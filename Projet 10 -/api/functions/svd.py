# functions/svd.py
import pandas as pd
from scipy.sparse.linalg import svds
import numpy as np

def load_and_prepare_svd_data(dataframe: pd.DataFrame):
    """
    Prépare les données à partir d'un DataFrame pour le filtrage collaboratif basé sur SVD.

    Args:
        dataframe (pd.DataFrame): Le DataFrame contenant les interactions utilisateur-article.

    Returns:
        tuple: Un tuple contenant le DataFrame, la matrice d'interaction,
               les IDs des utilisateurs et des articles.
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
    user_ids = interaction_matrix.index.tolist()
    article_ids = interaction_matrix.columns.tolist()
    return df_clean, interaction_matrix, user_ids, article_ids

def train_svd_model(interaction_matrix: pd.DataFrame, n_components: int = 50):
    """
    Entraîne un modèle SVD sur la matrice d'interaction.

    Args:
        interaction_matrix (pd.DataFrame): La matrice d'interaction utilisateur-article.
        n_components (int): Le nombre de composants latents pour SVD.

    Returns:
        tuple: Le modèle SVD (non utilisé directement ici mais potentiellement utile),
               les matrices U et Vt.
    """
    user_item_matrix = interaction_matrix.values
    mean_user_rating = user_item_matrix.mean(axis=1)
    user_item_matrix_normalized = user_item_matrix - mean_user_rating.reshape(-1, 1)

    # S'assurer que k est inférieur à la taille minimale de la matrice
    k = min(n_components, min(user_item_matrix_normalized.shape) - 1)
    U, sigma, Vt = svds(user_item_matrix_normalized, k=k)
    sigma = np.diag(sigma)
    return None, U, Vt # On ne retourne pas le modèle complet, mais les matrices dérivées

def get_svd_recommendations(user_id: int, dataframe: pd.DataFrame, interaction_matrix: pd.DataFrame, user_ids: list, article_ids: list, U_latent: np.ndarray, V_latent: np.ndarray, top_n: int = 5):
    """
    Génère des recommandations basées sur SVD pour un utilisateur donné.

    Args:
        user_id (int): L'ID de l'utilisateur.
        dataframe (pd.DataFrame): Le DataFrame original pour calculer la popularité.
        interaction_matrix (pd.DataFrame): La matrice d'interaction utilisée pour l'entraînement.
        user_ids (list): Liste des IDs des utilisateurs correspondant à U.
        article_ids (list): Liste des IDs des articles correspondant à V.
        U_latent (np.ndarray): Matrice U résultant de SVD.
        V_latent (np.ndarray): Matrice V transposée résultant de SVD.
        top_n (int): Le nombre de recommandations à retourner.

    Returns:
        list: Une liste de dictionnaires contenant 'article_id' et 'popularity'.
    """
    if user_id not in user_ids:
        # Si l'utilisateur est inconnu, retourner les articles populaires
        popular_articles = dataframe['click_article_id'].value_counts()
        top_articles = popular_articles.head(top_n)
        recommendations = [{"article_id": int(art_id), "popularity": int(count)} for art_id, count in top_articles.items()]
        return recommendations

    try:
        user_row_index = user_ids.index(user_id)
    except ValueError:
        # L'utilisateur n'est pas dans la liste des IDs connus du modèle
        # Cela ne devrait pas arriver si user_id est dans user_ids, mais on le gère quand même
        return []

    # Calcul de la prédiction pour l'utilisateur spécifique
    # Calculer la moyenne de l'utilisateur à partir de la matrice d'interaction originale
    mean_user_rating_matrix = interaction_matrix.mean(axis=1)
    mean_user_rating = mean_user_rating_matrix.loc[user_id]

    # Recalculer sigma à partir de U, Vt et de la matrice normalisée
    # On peut le recalculer comme ceci : sigma = U^T * (M - mean_user) * V
    # Mais c'est plus simple de le garder si on l'a.
    # Pour simplifier, on suppose qu'on peut recalculer sigma comme les valeurs singulières
    # En fait, svds retourne U, sigma, Vt. On a donc sigma.
    # Mais on l'a séparé dans train_svd_model.
    # Pour prédire, on fait U[user_idx] @ diag(sigma) @ Vt
    user_pred_scores = U_latent[user_row_index, :] @ V_latent # On omet sigma ici, ce qui est incorrect.
    # CORRECTION : On doit avoir sigma. On le recalcule ou on le passe.
    # Pour cette version, on va supposer qu'on peut le recalculer ou qu'on l'a gardé.
    # La fonction train_svd_model ne retourne pas sigma directement, mais on peut le faire ici.
    # On refait le calcul de SVD pour récupérer sigma, ce qui n'est pas optimal.
    # Une meilleure façon est de retourner sigma dans train_svd_model.
    # Modifions train_svd_model et get_svd_recommendations.
    # --- train_svd_model ---
    # def train_svd_model(interaction_matrix: pd.DataFrame, n_components: int = 50):
    #     user_item_matrix = interaction_matrix.values
    #     mean_user_rating = user_item_matrix.mean(axis=1)
    #     user_item_matrix_normalized = user_item_matrix - mean_user_rating.reshape(-1, 1)
    #     k = min(n_components, min(user_item_matrix_normalized.shape) - 1)
    #     U, sigma, Vt = svds(user_item_matrix_normalized, k=k)
    #     return None, U, Vt, sigma
    # --- get_svd_recommendations ---
    # def get_svd_recommendations(user_id: int, dataframe, interaction_matrix, user_ids, article_ids, U_latent, V_latent, sigma, top_n=5):
    #     ...
    #     user_pred_scores = U_latent[user_row_index, :] @ np.diag(sigma) @ V_latent
    #     ...
    # MAIS pour garder la signature demandée, on va recalculer sigma ici, ce qui est inefficace.
    # On fait SVD à nouveau.
    user_item_matrix_full = interaction_matrix.values
    mean_user_rating_full = user_item_matrix_full.mean(axis=1)
    user_item_matrix_normalized_full = user_item_matrix_full - mean_user_rating_full.reshape(-1, 1)
    _, sigma_full, _ = svds(user_item_matrix_normalized_full, k=U_latent.shape[1])
    sigma_diag = np.diag(sigma_full)

    user_pred_scores = U_latent[user_row_index, :] @ sigma_diag @ V_latent
    # Ajouter la moyenne de l'utilisateur
    user_pred_scores += mean_user_rating # Cette moyenne est scalaire pour l'utilisateur

    # Obtenir les indices des articles les mieux notés
    top_articles_indices = user_pred_scores.argsort()[-top_n:][::-1]
    recommended_article_ids = [article_ids[i] for i in top_articles_indices]

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
