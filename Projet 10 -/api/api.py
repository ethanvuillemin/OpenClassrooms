# api_main.py
from fastapi import FastAPI
from functions.popularity import get_popular_recommendations
from functions.item_based import load_and_prepare_data, get_item_based_collaborative_recommendations
from functions.session_based import  load_and_prepare_session_data, get_session_based_recommendations
from functions.svd import load_and_prepare_svd_data, train_svd_model, get_svd_recommendations
import pandas as pd

DATA_PATH = r"..\data\news-portal-user-interactions-by-globocom\clicks_sample.csv"
df = pd.read_csv(DATA_PATH, sep=',')
df = df.dropna(subset=['click_article_id'])

app = FastAPI()

@app.get("/")
async def alive():
    return {"message": "API de Recommandation Alive"}

@app.get("/recommendation/popularity")
async def recommendation_per_popularity():
    recommendations = get_popular_recommendations(dataframe=df, top_n=5)
    return {"recommendations": recommendations}

@app.get("/recommendation/item-based")
async def recommendation_item_based(user_id: int):
    clicks_df, interaction_matrix = load_and_prepare_data(dataframe=df)

    if not interaction_matrix.empty:
        recommendations = get_item_based_collaborative_recommendations(user_id, dataframe=df, interaction_matrix=interaction_matrix, top_n=5)
        return {"user_id": user_id, "recommendations": recommendations}
    else:
        return {"user_id": user_id, "recommendations": []}

@app.get("/recommendation/session-based") # Corrigé la typo
async def recommendation_per_session(user_id: str):
    clicks_df = load_and_prepare_session_data(dataframe=df)
    if not clicks_df.empty:
        recommendations = get_session_based_recommendations(user_id, dataframe=df, top_n=5)
        return {"user_id": user_id, "recommendations": recommendations}
    else:
        return {"user_id": user_id, "recommendations": []}

@app.get("/recommendation/svd")
async def recommendation_per_svd(user_id: int):
    clicks_df, interaction_matrix, user_ids, article_ids = load_and_prepare_svd_data(dataframe=df)
    svd_model, U_latent, V_latent = train_svd_model(interaction_matrix, n_components=50)

    if user_id in user_ids:
        recommendations = get_svd_recommendations(user_id, dataframe=df, interaction_matrix=interaction_matrix, user_ids=user_ids, article_ids=article_ids, U_latent=U_latent, V_latent=V_latent, top_n=5)
        return {"user_id": user_id, "recommendations": recommendations}
    else:
        # Si l'utilisateur n'est pas dans les données d'entraînement, on retombe sur la popularité
        popular_articles = df['click_article_id'].value_counts()
        top_articles = popular_articles.head(5)
        fallback_recs = [{"article_id": int(art_id), "popularity": int(count)} for art_id, count in top_articles.items()]
        return {"user_id": user_id, "recommendations": fallback_recs, "info": "Utilisateur inconnu du modèle SVD, retombé sur la popularité."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app=app, host="0.0.0.0", port=8005) # Utilise un int pour le port
