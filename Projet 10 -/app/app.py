import gradio as gr
import pandas as pd
import requests
import time

# --- Configuration de l'API ---
API_BASE_URL = "http://localhost:8005"

def call_api(endpoint, params=None):
    url = f"{API_BASE_URL}{endpoint}"
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Erreur API : {e}")
        return None

def get_recommendations_from_api(user_id_str, algo_choice):
    # Animation de chargement
    time.sleep(0.5)

    try:
        user_id = int(user_id_str)
    except ValueError:
        return (
            pd.DataFrame(columns=['Rang', 'ID Article', 'Popularité (clics)']),
            "❌ **Erreur** : L'ID utilisateur doit être un nombre entier.",
            "error"
        )

    # Mapping des algorithmes et endpoints
    algo_map = {
        "Recommandation basée sur la popularité": {
            "endpoint": "/recommendation/popularity",
            "method": "Popularité Globale 🌍",
            "params": None
        },
        "Filtrage Collaboratif Basé sur les Items": {
            "endpoint": "/recommendation/item-based",
            "method": "Item-Based Collaborative Filtering 🔍",
            "params": {"user_id": user_id}
        },
        "Filtrage Collaboratif Basé sur les Sessions": {
            "endpoint": "/recommendation/session-based",
            "method": "Session-Based Recommendation 🕒",
            "params": {"user_id": str(user_id)}
        },
        "Filtrage Collaboratif Basé sur SVD": {
            "endpoint": "/recommendation/svd",
            "method": "SVD (Décomposition en Valeurs Singulières) 📊",
            "params": {"user_id": user_id}
        }
    }

    config = algo_map.get(algo_choice)
    if not config:
        return (
            pd.DataFrame(columns=['Rang', 'ID Article', 'Popularité (clics)']),
            "❌ **Erreur** : Algorithme inconnu. Veuillez sélectionner une option valide.",
            "error"
        )

    api_response = call_api(config["endpoint"], config["params"])
    if api_response is None:
        return (
            pd.DataFrame(columns=['Rang', 'ID Article', 'Popularité (clics)']),
            f"⚠️ **Erreur API** : Impossible de récupérer les recommandations pour {config['method']}.",
            "error"
        )

    # Construction du DataFrame
    recommendations = api_response.get('recommendations', [])
    results = []
    for i, rec in enumerate(recommendations, 1):
        if isinstance(rec, dict) and 'article_id' in rec:
            results.append({
                'Rang': i,
                'ID Article': rec['article_id'],
                'Popularité (clics)': rec.get('popularity', 0)
            })

    df = pd.DataFrame(results)
    user_status = f"👤 **Utilisateur** : ID {user_id} traité avec succès !"
    info_text = f"""
    ✨ **Méthode** : {config['method']}
    {user_status}
    📊 **Nombre de recommandations** : {len(df)}
    """

    return df, info_text, "success"

# --- Interface Gradio (Version PSM) ---
with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="purple",
        secondary_hue="blue",
        font=["Inter", "ui-sans-serif"]
    ),
    title="My Content 🚀 | Recommandations PSM",
    css="""
    .gradio-container { max-width: 1000px !important; }
    .header { text-align: center; margin-bottom: 1rem; }
    .footer { text-align: center; margin-top: 2rem; font-size: 0.9rem; color: gray; }
    .success { color: green; }
    .error { color: red; }
    .warning { color: orange; }
    """
) as app:
    # --- En-tête ---
    gr.Markdown("""
    <div class="header">
        # 📢 **My Content | Système de Recommandation PSM**
        *Powered by AI & Data Science*
    </div>
    """)

    # --- Corps ---
    with gr.Row(equal_height=True):
        # Colonne de gauche : Paramètres
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ **Paramètres**")
            user_input = gr.Textbox(
                label="ID Utilisateur",
                value="1",
                info="Entrez un ID utilisateur (ex: 123).",
                placeholder="123",
                elem_classes="input-box"
            )
            algo_selector = gr.Dropdown(
                label="Algorithme de Recommandation",
                choices=[
                    "Recommandation basée sur la popularité",
                    "Filtrage Collaboratif Basé sur les Items",
                    "Filtrage Collaboratif Basé sur les Sessions",
                    "Filtrage Collaboratif Basé sur SVD"
                ],
                value="Recommandation basée sur la popularité",
                info="Sélectionnez la méthode de recommandation.",
                elem_classes="dropdown-box"
            )
            run_btn = gr.Button(
                "🚀 **Générer les Recommandations**",
                variant="primary",
                scale=1
            )

        # Colonne de droite : Résultats
        with gr.Column(scale=2):
            gr.Markdown("### 📊 **Résultats**")
            output_info = gr.Markdown(
                label="Statut de la requête",
                elem_classes="output-info"
            )
            output_df = gr.DataFrame(
                label="Articles Recommandés",
                headers=["Rang", "ID Article", "Popularité (clics)"],
                datatype=["number", "number", "number"],
                elem_classes="output-df"
            )

    # --- Pied de page ---
    gr.Markdown("""
    <div class="footer">
        🔹 **My Content PSM v3.0** | *Recommandations intelligentes pour maximiser l'engagement*
    </div>
    """)

    # --- Logique d'interaction ---
    run_btn.click(
        fn=get_recommendations_from_api,
        inputs=[user_input, algo_selector],
        outputs=[output_df, output_info],
        api_name="generate_recommendations"
    )

# --- Lancement ---
if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
