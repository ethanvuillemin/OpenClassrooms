import streamlit as st
from chatbot import RuleBasedChatbot
import json
import re

# Initialisation du chatbot
chatbot = RuleBasedChatbot('rules.json')

# Charger les questions suggérées
with open('rules.json', 'r', encoding='utf-8') as f:
    rules_data = json.load(f)
    suggested_questions = [intent['patterns'][0] for intent in rules_data['intents']]

# --- Configuration de la page ---
st.set_page_config(page_title="Chatbot Python", page_icon="💬", layout="centered")

# --- CSS personnalisé pour un rendu moderne ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    body {
        font-family: 'Roboto', sans-serif;
        background-color: #f5f7fa;
    }

    .main-title {
        text-align: center;
        color: #2e3b4e;
        font-weight: 700;
    }

    .suggestion-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 12px;
        margin-bottom: 20px;
    }

    .suggestion-button {
        background-color: #4a90e2;
        color: white;
        padding: 10px 15px;
        border-radius: 12px;
        border: none;
        cursor: pointer;
        font-size: 14px;
        transition: background-color 0.3s ease;
    }

    .suggestion-button:hover {
        background-color: #357ABD;
    }

    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-bottom: 20px;
    }

    .chat-bubble {
        padding: 10px 15px;
        border-radius: 15px;
        max-width: 70%;
        line-height: 1.5;
        white-space: pre-wrap;
    }

    .chat-bubble-user {
        background-color: #dcf8c6;
        align-self: flex-end;
        color: #333;
    }

    .chat-bubble-assistant {
        background-color: #ffffff;
        align-self: flex-start;
        color: #333;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- Titre ---
st.markdown("<h1 class='main-title'>💬 Chatbot Python</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:16px;'>Posez des questions sur la syntaxe ou les fonctionnalités de Python</p>",
            unsafe_allow_html=True)

# --- Historique des messages ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Je suis votre assistant pour Python. Que voulez-vous savoir ?"}
    ]

# --- Affichage des bulles de chat ---
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"<div class='chat-bubble chat-bubble-user'>{message['content']}</div>", unsafe_allow_html=True)
    else:
        # On affiche le texte, et les blocs de code avec st.code()
        text_blocks = re.split(r'(```.*?```)', message['content'], flags=re.DOTALL)
        st.markdown(f"<div class='chat-bubble chat-bubble-assistant'>", unsafe_allow_html=True)
        for block in text_blocks:
            if block.strip().startswith('```'):
                lang = block[3:].split('\n', 1)[0].strip()  # Récupérer le langage
                code_content = block.split('\n', 1)[1].rstrip('`').strip()
                st.code(code_content, language=lang if lang else "python")
            elif block.strip():
                st.markdown(block.strip())
        st.markdown("</div>", unsafe_allow_html=True)

# --- Boutons de questions suggérées ---
st.markdown("<div class='suggestion-container'>", unsafe_allow_html=True)
for i, question in enumerate(suggested_questions[:12]):  # Limiter à 12 questions
    if st.button(question, key=f"btn_{i}", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": question})
        response = chatbot.get_response(question)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# --- Zone de saisie utilisateur ---
if prompt := st.chat_input("Votre question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f"<div class='chat-bubble chat-bubble-user'>{prompt}</div>", unsafe_allow_html=True)

    response = chatbot.get_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Affichage de la réponse avec gestion des blocs de code
    text_blocks = re.split(r'(```.*?```)', response, flags=re.DOTALL)
    st.markdown(f"<div class=''>", unsafe_allow_html=True)
    for block in text_blocks:
        if block.strip().startswith('```'):
            lang = block[3:].split('\n', 1)[0].strip()  # Récupérer le langage
            code_content = block.split('\n', 1)[1].rstrip('`').strip()
            st.code(code_content, language=lang if lang else "python")
        elif block.strip():
            st.markdown(block.strip())
    st.markdown("</div>", unsafe_allow_html=True)