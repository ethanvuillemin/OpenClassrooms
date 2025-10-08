import chainlit as cl
from mistralai import Mistral
import os

# Initialiser le client Mistral
client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY"))

# Configuration du modèle
MODEL = "mistral-large-latest"

@cl.on_chat_start
async def start():
    """Fonction appelée au démarrage du chat"""
    # Initialiser l'historique de conversation
    cl.user_session.set("message_history", [])
    
    await cl.Message(
        content="👋 Bienvenue ! Je suis connecté à Mistral AI. Posez-moi n'importe quelle question !"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Fonction appelée à chaque message de l'utilisateur"""
    
    # Récupérer l'historique
    message_history = cl.user_session.get("message_history")
    
    # Ajouter le message de l'utilisateur
    message_history.append({
        "role": "user",
        "content": message.content
    })
    
    # Créer un message vide pour le streaming
    msg = cl.Message(content="")
    await msg.send()
    
    try:
        # Appeler l'API Mistral avec streaming
        stream_response = client.chat.stream(
            model=MODEL,
            messages=message_history
        )
        
        full_response = ""
        
        # Streamer la réponse
        for chunk in stream_response:
            if chunk.data.choices[0].delta.content:
                content = chunk.data.choices[0].delta.content
                full_response += content
                await msg.stream_token(content)
        
        # Finaliser le message
        await msg.update()
        
        # Ajouter la réponse à l'historique
        message_history.append({
            "role": "assistant",
            "content": full_response
        })
        
        # Mettre à jour l'historique dans la session
        cl.user_session.set("message_history", message_history)
        
    except Exception as e:
        await msg.update()
        await cl.Message(
            content=f"❌ Erreur : {str(e)}\n\nAssurez-vous que votre clé API Mistral est configurée correctement."
        ).send()

@cl.on_chat_end
def end():
    """Fonction appelée à la fin du chat"""
    print("Chat terminé !")