import chainlit as cl
from rag_simple_ import LangGraphRAG
import os
import re
from dotenv import load_dotenv

load_dotenv()

# Variable globale pour stocker l'instance RAG
rag_instance = None

# Définition des personas
PERSONAS = {
    "expert_juridique": {
        "name": "🎓 Expert Juridique",
        "description": "Analyses approfondies avec références précises aux articles",
        "system_prompt": "Tu es un expert en droit civil français. Fournis des analyses juridiques détaillées avec références précises aux articles du Code Civil. Utilise un langage juridique approprié.",
        "icon": "🎓",
        "color": "#1976D2"
    },
    "vulgarisateur": {
        "name": "💬 Vulgarisateur",
        "description": "Explications simples et accessibles pour tous",
        "system_prompt": "Tu es un vulgarisateur juridique. Explique le droit civil de manière simple et accessible, en utilisant des exemples concrets du quotidien. Évite le jargon juridique complexe.",
        "icon": "💬",
        "color": "#4CAF50"
    },
    "conseiller_pratique": {
        "name": "💼 Conseiller Pratique",
        "description": "Conseils pratiques et solutions concrètes",
        "system_prompt": "Tu es un conseiller juridique pratique. Fournis des conseils concrets et des solutions applicables, en te basant sur le Code Civil. Mets l'accent sur les démarches et implications pratiques.",
        "icon": "💼",
        "color": "#FF9800"
    },
    "enseignant": {
        "name": "👨‍🏫 Enseignant",
        "description": "Approche pédagogique avec exemples et exercices",
        "system_prompt": "Tu es un professeur de droit civil. Adopte une approche pédagogique, structure tes explications de manière claire, propose des exemples et des cas pratiques pour faciliter la compréhension.",
        "icon": "👨‍🏫",
        "color": "#9C27B0"
    }
}

# Exemples de prompts par catégorie
PROMPT_EXAMPLES = {
    "📄 Contrats": [
        "Quelles sont les conditions de validité d'un contrat ?",
        "Qu'est-ce qu'un vice du consentement ?",
        "Comment se forme un contrat ?",
        "Quelle est la différence entre nullité absolue et relative ?"
    ],
    "⚖️ Responsabilité": [
        "Qu'est-ce que la responsabilité civile délictuelle ?",
        "Quelles sont les conditions de la responsabilité du fait des choses ?",
        "Comment fonctionne la responsabilité du fait d'autrui ?",
        "Qu'est-ce que le préjudice moral ?"
    ],
    "🏠 Propriété": [
        "Comment se définit le droit de propriété ?",
        "Qu'est-ce que l'usufruit ?",
        "Quelles sont les servitudes légales ?",
        "Comment se transmet la propriété immobilière ?"
    ],
    "👨‍👩‍👧 Famille": [
        "Quelles sont les conditions du mariage ?",
        "Comment fonctionne le régime de la communauté ?",
        "Qu'est-ce que l'autorité parentale ?",
        "Quelles sont les règles sur le divorce ?"
    ],
    "💰 Successions": [
        "Qui sont les héritiers légaux ?",
        "Comment rédiger un testament ?",
        "Qu'est-ce que la réserve héréditaire ?",
        "Comment se partage une succession ?"
    ]
}

@cl.on_chat_start
async def start():
    global rag_instance
    
    # Vérifier l'existence du vectorstore
    vectorstore_path = os.getenv("VECTORSTORE")
    if not os.path.exists(vectorstore_path):
        await cl.Message(
            content="⚠️ Le vectorstore n'existe pas. Veuillez d'abord le créer avec un script dédié."
        ).send()
        return

    # Initialiser la session
    cl.user_session.set("conversation_count", 0)
    cl.user_session.set("persona_selected", False)
    
    # Message de bienvenue
    welcome_msg = """# 🇫🇷 Assistant Code Civil Français

Votre assistant juridique intelligent propulsé par IA

---

## 🎯 Commencez par choisir votre assistant
"""
    
    await cl.Message(content=welcome_msg).send()
    
    # Créer les settings pour le choix du persona
    settings = await cl.ChatSettings(
        [
            cl.input_widget.Select(
                id="persona",
                label="🎭 Choisissez votre persona",
                values=[key for key in PERSONAS.keys()],
                initial_value="expert_juridique",
            ),
            cl.input_widget.Select(
                id="category",
                label="📚 Catégorie de questions",
                values=list(PROMPT_EXAMPLES.keys()),
                initial_value=list(PROMPT_EXAMPLES.keys())[0],
            ),
        ]
    ).send()
    
    # Afficher les personas disponibles
    personas_info = "\n\n**Personas disponibles :**\n\n"
    for key, persona in PERSONAS.items():
        personas_info += f"{persona['icon']} **{persona['name']}**\n_{persona['description']}_\n\n"
    
    await cl.Message(content=personas_info).send()
    
    # Afficher un exemple pour chaque catégorie
    await show_example_prompts()

@cl.on_settings_update
async def setup_agent(settings):
    """Callback appelé quand les settings changent"""
    global rag_instance
    
    persona_key = settings["persona"]
    category = settings.get("category", list(PROMPT_EXAMPLES.keys())[0])
    
    # Stocker le persona sélectionné
    cl.user_session.set("current_persona", persona_key)
    cl.user_session.set("current_category", category)
    
    persona = PERSONAS[persona_key]
    
    # Initialiser le RAG si pas encore fait
    if rag_instance is None:
        try:
            msg = cl.Message(content="⏳ **Initialisation du système RAG...**")
            await msg.send()
            
            rag_instance = LangGraphRAG(
                pdf_path="./data/code-civil",
                embedding_model_path=os.getenv("EMBEDDING_MODEL"),
                vectorstore_path=os.getenv("VECTORSTORE")
            )
            cl.user_session.set("rag", rag_instance)
            cl.user_session.set("persona_selected", True)
            
            msg.content = f"✅ **Système initialisé avec succès !**"
            await msg.update()
            
        except Exception as e:
            await cl.Message(
                content=f"❌ **Erreur lors de l'initialisation :** {str(e)}"
            ).send()
            return
    else:
        cl.user_session.set("persona_selected", True)
    
    # Message de confirmation
    confirmation_msg = f"""
✅ **Configuration mise à jour**

**Persona actif :** {persona['icon']} {persona['name']}
**Catégorie :** {category}

{persona['description']}

💡 Posez votre question ou utilisez les boutons ci-dessous pour des exemples !
"""
    
    await cl.Message(content=confirmation_msg).send()
    
    # Afficher les exemples de la catégorie sélectionnée
    await show_category_examples(category)

async def show_example_prompts():
    """Affiche tous les exemples de prompts disponibles"""
    examples_msg = "\n## 💡 Exemples de questions par catégorie\n\n"
    
    for category, examples in PROMPT_EXAMPLES.items():
        examples_msg += f"\n**{category}**\n"
        for example in examples[:2]:
            examples_msg += f"• {example}\n"
    
    examples_msg += "\n\n👆 **Utilisez le menu des paramètres (⚙️) pour choisir votre persona et catégorie**"
    
    await cl.Message(content=examples_msg).send()

async def show_category_examples(category):
    """Affiche les exemples d'une catégorie spécifique sous forme de boutons"""
    if category not in PROMPT_EXAMPLES:
        return
    
    examples = PROMPT_EXAMPLES[category]
    examples_msg = f"\n**{category} - Exemples de questions :**\n\n"
    
    for i, example in enumerate(examples):
        examples_msg += f"{i+1}. {example}\n"
    
    examples_msg += "\n💬 **Copiez-collez une question ou posez la vôtre !**"
    
    await cl.Message(content=examples_msg).send()

@cl.on_message
async def main(message: cl.Message):
    # Vérifier si le RAG est initialisé
    if not cl.user_session.get("persona_selected", False):
        await cl.Message(
            content="⚠️ **Veuillez d'abord configurer votre assistant**\n\n👉 Utilisez le menu des paramètres (⚙️ en haut à droite) pour choisir votre persona."
        ).send()
        return
    
    await process_message(message.content)

async def process_message(content: str):
    rag = cl.user_session.get("rag")
    if rag is None:
        await cl.Message(content="❌ Le système RAG n'est pas initialisé.").send()
        return

    # Récupérer le persona actuel
    current_persona_key = cl.user_session.get("current_persona", "expert_juridique")
    current_persona = PERSONAS[current_persona_key]
    
    # Incrémenter le compteur
    count = cl.user_session.get("conversation_count", 0) + 1
    cl.user_session.set("conversation_count", count)
    
    # Message de traitement avec style
    msg = cl.Message(content="")
    await msg.send()
    
    # Indicateur de traitement
    processing_msgs = [
        "🔍 Recherche dans le Code Civil...",
        "📚 Analyse des articles pertinents...",
        "💭 Génération de la réponse...",
    ]
    
    for proc_msg in processing_msgs:
        await msg.stream_token(f"{proc_msg}\n")
    
    await msg.stream_token(f"\n---\n\n**{current_persona['icon']} Réponse de {current_persona['name']} :**\n\n")

    try:
        # Ajouter le system prompt du persona
        enhanced_query = f"{current_persona['system_prompt']}\n\nQuestion: {content}"
        
        response = await cl.make_async(rag.invoke)(enhanced_query)
        
        cl.user_session.set("full_response", response)
        cl.user_session.set("last_query", content)
        
        # Extraire la réponse finale
        final_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
        
        # Streaming de la réponse
        for i in range(0, len(final_response), 500):
            chunk = final_response[i:i+500]
            await msg.stream_token(chunk)
        
        await msg.update()
        
        # Message post-réponse avec actions
        post_msg = f"""

---

## 🎯 Actions disponibles

Utilisez les boutons ci-dessous ou tapez :
• **`sources`** - 📚 Voir les articles du Code Civil référencés
• **`reflexion`** - 🧠 Comprendre le processus de réflexion de l'IA
• **`exemples`** - 💡 Obtenir des questions similaires
• **`stats`** - 📊 Voir vos statistiques de session

Ou changez de persona/catégorie via le menu ⚙️
"""
        
        await cl.Message(content=post_msg).send()
        
        # Stats périodiques
        if count % 3 == 0:
            await cl.Message(
                content=f"📊 **{count} questions posées** avec {current_persona['icon']} {current_persona['name']}"
            ).send()
        
        # Traiter les commandes spéciales
        if content.lower() in ["sources", "source"]:
            await show_sources()
        elif content.lower() in ["reflexion", "réflexion", "think"]:
            await show_reflection()
        elif content.lower() in ["exemples", "exemple", "similaire"]:
            await show_related_questions()
        elif content.lower() in ["stats", "statistiques"]:
            await show_stats()
            
    except Exception as e:
        await cl.Message(content=f"❌ **Erreur :** {str(e)}").send()

async def show_sources():
    full_response = cl.user_session.get("full_response", "")
    articles = re.findall(r'[Aa]rticle\s+\d+(?:-\d+)?', full_response)
    
    if articles:
        unique_articles = sorted(list(set(articles)))
        sources_msg = "📚 **Articles du Code Civil référencés :**\n\n"
        for art in unique_articles[:15]:
            sources_msg += f"• {art}\n"
        
        if len(unique_articles) > 15:
            sources_msg += f"\n... et {len(unique_articles) - 15} autres articles"
    else:
        sources_msg = "ℹ️ Aucune référence d'article spécifique trouvée dans cette réponse."
    
    await cl.Message(content=sources_msg).send()

async def show_reflection():
    full_response = cl.user_session.get("full_response", "")
    think_match = re.search(r'<think>(.*?)</think>', full_response, re.DOTALL)
    
    if think_match:
        reflection_msg = f"""🧠 **Processus de réflexion de l'IA :**

```
{think_match.group(1).strip()}
```

💡 Ce processus montre comment l'IA a analysé votre question avant de répondre.
"""
    else:
        reflection_msg = "ℹ️ Aucun processus de réflexion disponible pour cette réponse."
    
    await cl.Message(content=reflection_msg).send()

async def show_related_questions():
    last_query = cl.user_session.get("last_query", "")
    current_category = cl.user_session.get("current_category", list(PROMPT_EXAMPLES.keys())[0])
    
    # Essayer de trouver la catégorie pertinente
    related = []
    for category, examples in PROMPT_EXAMPLES.items():
        if any(word in last_query.lower() for word in category.lower().split()):
            related = examples
            break
    
    if not related:
        related = PROMPT_EXAMPLES.get(current_category, PROMPT_EXAMPLES["📄 Contrats"])
    
    related_msg = "💡 **Questions similaires que vous pourriez poser :**\n\n"
    for i, q in enumerate(related[:5], 1):
        related_msg += f"{i}. {q}\n"
    
    related_msg += "\n💬 Copiez-collez une question ou reformulez la vôtre !"
    
    await cl.Message(content=related_msg).send()

async def show_stats():
    count = cl.user_session.get("conversation_count", 0)
    persona_key = cl.user_session.get("current_persona", "expert_juridique")
    persona = PERSONAS[persona_key]
    category = cl.user_session.get("current_category", "Non définie")
    
    stats_msg = f"""📊 **Statistiques de votre session**

• **Questions posées :** {count}
• **Persona actif :** {persona['icon']} {persona['name']}
• **Catégorie :** {category}

Continuez à explorer le Code Civil français ! 🇫🇷
"""
    
    await cl.Message(content=stats_msg).send()

@cl.on_chat_end
async def end():
    count = cl.user_session.get("conversation_count", 0)
    persona_key = cl.user_session.get("current_persona", "expert_juridique")
    persona_name = PERSONAS[persona_key]["name"]
    
    await cl.Message(
        content=f"""# 👋 Merci d'avoir utilisé l'Assistant Code Civil !

## 📊 Récapitulatif de votre session

• **{count} questions posées**
• **Persona utilisé :** {persona_name}

---

💡 **Astuce :** Vos préférences seront sauvegardées pour votre prochaine visite !

À bientôt pour de nouvelles questions juridiques ! 🇫🇷⚖️
"""
    ).send()