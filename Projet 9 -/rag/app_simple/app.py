import os
import json
import chainlit as cl
from dotenv import load_dotenv
from rag_simple import create_simple_rag_graph
from rag_avance import create_advanced_rag_graph

# Chargement des variables d'environnement
load_dotenv()

# Chargement des fichiers de configuration
with open("personas.json", "r") as f:
    personas_data = json.load(f)
    personas = personas_data["personas"]
    # Créer un dictionnaire pour un accès rapide par ID
    persona_dict = {p["id"]: p for p in personas}

with open("prompts.json", "r") as f:
    prompts_data = json.load(f)
    prompts = prompts_data["prompts"]

# Initialisation des graphes RAG
simple_rag = create_simple_rag_graph()
advanced_rag = create_advanced_rag_graph()

# État de la session utilisateur
@cl.on_chat_start
async def start():
    # Initialisation de la session
    cl.user_session.set("model", "simple")  # Par défaut: modèle simple
    cl.user_session.set("persona", persona_dict[personas[0]["id"]])  # Par défaut: premier persona
    cl.user_session.set("history", [])  # Historique des conversations

    # --- Configuration via ChatSettings ---
    # La syntaxe correcte pour les éléments de ChatSettings est souvent `cl.inputs.Select`, `cl.inputs.Switch`, etc.
    # ou directement `Select`, `Switch` dans certains cas
    # Selon la documentation Chainlit, c'est `Select` ou `cl.inputs.Select`
    # Essayons `cl.Select` ou `cl.inputs.Select` à l'intérieur de la liste
    # La syntaxe est : cl.ChatSettings([cl.inputs.Select(...), cl.inputs.Select(...)])
    # ou peut-être : cl.ChatSettings([Select(...), Select(...)])
    # Essayons avec cl.inputs.Select
    try:
        # Essaye cette syntaxe d'abord (la plus courante)
        settings = cl.ChatSettings(
            [
                cl.inputs.Select( # Utilisation de cl.inputs.Select
                    id="model_type",
                    label="Modèle RAG",
                    values=["simple", "avance"],
                    initial_index=0, # Par défaut: simple
                ),
                cl.inputs.Select( # Utilisation de cl.inputs.Select
                    id="selected_persona",
                    label="Persona",
                    values=[p["name"] for p in personas], # Liste des noms
                    initial_index=0, # Par défaut: premier
                ),
            ]
        )
    except AttributeError:
        # Si cl.inputs.Select échoue, essaye sans le préfixe cl.inputs
        settings = cl.ChatSettings(
            [
                cl.Select( # Utilisation de cl.Select
                    id="model_type",
                    label="Modèle RAG",
                    values=["simple", "avance"],
                    initial_index=0,
                ),
                cl.Select( # Utilisation de cl.Select
                    id="selected_persona",
                    label="Persona",
                    values=[p["name"] for p in personas],
                    initial_index=0,
                ),
            ]
        )
    await settings.send()

    # Message de bienvenue
    welcome_msg = cl.Message(
        content="",
        elements=[
            cl.Text(name="intro", content="Bienvenue dans l'assistant juridique basé sur le Code civil français ! 📜", display="inline"),
            cl.Text(name="instructions", content="\n\nConfigurez votre session à l'aide des paramètres en haut à droite (⚙️). Posez ensuite votre question ou utilisez un exemple ci-dessous.", display="inline")
        ]
    )
    await welcome_msg.send()

    # Affichage des prompts d'exemple
    await cl.Message(
        content="**Exemples de questions :**",
        elements=[
            cl.Text(name=f"prompt_{i}", content=f"- {prompt}", display="inline")
            for i, prompt in enumerate(prompts[:5])  # Limiter à 5 exemples pour ne pas surcharger
        ]
    ).send()

    # Boutons pour utiliser les exemples
    example_actions = [
        cl.Action(name="use_prompt", value=prompt, label=f"💬 {prompt[:50]}...", payload={})
        for prompt in prompts[:5]  # Limiter à 5 exemples
    ]
    if example_actions:
        await cl.Message(
            content="",
            actions=example_actions
        ).send()

# Callback pour les changements de paramètres
@cl.on_settings_update
async def setup_agent(settings):
    print("Settings updated to: ", settings)

    model_type = settings["model_type"]
    persona_name = settings["selected_persona"]

    # Mettre à jour la session
    cl.user_session.set("model", model_type)
    # Trouver le persona par nom
    persona = next((p for p in personas if p["name"] == persona_name), persona_dict[personas[0]["id"]]) # Retour au premier si non trouvé
    cl.user_session.set("persona", persona)

    # Confirmation visuelle
    await cl.Message(
        content=f"Configuration mise à jour :\n- Modèle : **{model_type}**\n- Persona : **{persona['name']}**"
    ).send()


# Utilisation d'un prompt d'exemple
@cl.action_callback("use_prompt")
async def on_use_prompt(action: cl.Action):
    # Correction : Utilisation de action.value pour les prompts (stocké dans 'value' lors de la création)
    # Si action.value n'existe pas, essayons action.id
    try:
        query = action.value
    except AttributeError:
        query = action.id
    await process_query(query)

# Traitement d'une requête utilisateur
async def process_query(query):
    model_type = cl.user_session.get("model")
    persona = cl.user_session.get("persona")

    # Affichage de la question avec mise en forme
    question_msg = cl.Message(
        content=f"**Question :** {query}",
        author="user" # Optionnel : change l'auteur
    )
    await question_msg.send()

    # Initialisation du message pour la réponse avec un indicateur de chargement
    response_msg = cl.Message(
        content="",
        author="assistant" # Optionnel : change l'auteur
    )
    await response_msg.send()

    # Sélection du modèle RAG
    if model_type == "simple":
        rag = simple_rag
        state = {
            "question": query,
            "documents": [],  # À remplacer par vos documents réels
            "retrieved_docs": [],
            "answer": "",
            "error": None
        }
    else:
        rag = advanced_rag
        state = {
            "original_question": query,
            "rewritten_queries": [],
            "query_type": "",
            "documents": [],  # À remplacer par vos documents réels
            "retrieved_docs_semantic": [],
            "retrieved_docs_lexical": [],
            "merged_docs": [],
            "reranked_docs": [],
            "answer": "",
            "confidence_score": 0.0,
            "validation_result": {},
            "cache_hit": False,
            "error": None
        }

    # Exécution du modèle RAG
    try:
        result = rag.invoke(state)
        answer = result.get("answer", "Désolé, je n'ai pas pu générer de réponse.")
        response_msg.content = f"**Réponse :** {answer}" # Mise en forme de la réponse
        await response_msg.update() # Mise à jour du message avec la réponse complète

        # Bouton d'évaluation
        eval_action = cl.Action(
            name="evaluate",
            value=json.dumps({"query": query, "response": answer}),
            label="📝 Évaluer cette réponse",
            payload={}
        )
        await response_msg.update(actions=[eval_action])

    except Exception as e:
        response_msg.content = f"**Erreur :** Une erreur est survenue : {str(e)}"
        await response_msg.update() # Mise à jour du message avec l'erreur


# Évaluation de la réponse
@cl.action_callback("evaluate")
async def on_evaluate(action: cl.Action):
    # Récupération des données de la réponse évaluée
    try:
        # Essayons d'abord action.value (ancienne méthode, mais peut-être rétablie pour evaluate)
        data = json.loads(action.value)
    except AttributeError:
        # Si action.value n'existe pas, essayons action.id
        try:
            data = json.loads(action.id)
        except AttributeError:
            # Si action.id non plus, essayons payload
            try:
                data = json.loads(action.payload.get("value"))
            except (AttributeError, TypeError):
                await cl.Message(content="Erreur: Impossible de récupérer les données d'évaluation.").send()
                return

    eval_msg = cl.Message(
        content=f"**Évaluation de :** {data['query']}",
        elements=[
            cl.Text(name="response_to_eval", content=f"**Réponse :** {data['response']}", display="inline")
        ]
    )
    await eval_msg.send()

    # Demande de la note
    note_resp = await cl.AskUserMessage(content="**Notez la réponse (1-5) :**", timeout=60).send()
    if not note_resp:
        await cl.Message(content="Temps écoulé pour la note.").send()
        return
    note = note_resp["content"]

    # Demande de la justification
    justification_resp = await cl.AskUserMessage(content="**Justifiez votre note :**", timeout=120).send()
    if not justification_resp:
        await cl.Message(content="Temps écoulé pour la justification.").send()
        return
    justification = justification_resp["content"]

    # Enregistrement de l'évaluation
    evaluation = {
        "note": note,
        "justification": justification
    }

    history = cl.user_session.get("history")
    history.append({
        "query": data["query"],
        "response": data["response"],
        "evaluation": evaluation
    })
    cl.user_session.set("history", history)

    # Confirmation de l'évaluation
    await cl.Message(
        content=f"Merci pour votre évaluation ! 🙌\nNote : {note}/5\nJustification : {justification}"
    ).send()

# Affichage de l'historique (optionnel, peut être ajouté via un bouton global)
@cl.action_callback("show_history")
async def on_show_history(action: cl.Action):
    history = cl.user_session.get("history")
    if not history:
        await cl.Message(content="Aucun historique disponible.").send()
        return

    history_msg_content = "**Historique des évaluations :**\n\n"
    for i, entry in enumerate(history):
        history_msg_content += (
            f"--- Évaluation {i+1} ---\n"
            f"**Question :** {entry['query']}\n"
            f"**Réponse :** {entry['response']}\n"
            f"**Évaluation :** {entry['evaluation']['note']}/5\n"
            f"**Justification :** {entry['evaluation']['justification']}\n\n"
        )

    await cl.Message(content=history_msg_content).send()
