# POC Code Civil Français avec Chainlit et LangGraph

![Chainlit](https://img.shields.io/badge/Chainlit-1.0.0-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-0.0.10-green)
![Python](https://img.shields.io/badge/Python-3.9%2B-yellow)

Une **POC (Preuve de Concept)** pour explorer et interagir avec le **Code civil français** via une interface intuitive, en utilisant **Chainlit** pour l'UI et **LangGraph** pour implémenter deux modèles RAG (Retrieval-Augmented Generation) modulaires.

---

## 📌 **Contexte**
Ce projet vise à fournir une interface conviviale pour poser des questions sur le **Code civil français**, avec :
- Deux modèles RAG distincts (stratégies de récupération/génération différentes).
- Un système de **personas juridiques** pour adapter le ton et la complexité des réponses.
- Un historique des conversations et une évaluation structurée des réponses.

---

## 📂 **Structure du Projet**

```
/code_civil_poc/
│
├── app.py                  # Interface utilisateur Chainlit
├── rag1.py                 # Modèle RAG 1 (LangGraph)
├── rag2.py                 # Modèle RAG 2 (LangGraph)
├── personas.json           # Liste des personas juridiques
├── prompts.json            # Liste des prompts d'exemple
├── requirements.txt        # Dépendances Python
└── README.md               # Documentation du projet
```

---

## 🔧 **Fonctionnalités Clés**

| Fonctionnalité                     | Description                                                                                     |
|-------------------------------------|-------------------------------------------------------------------------------------------------|
| **Sélection de modèle RAG**         | Choix entre deux modèles RAG avec des stratégies différentes.                                  |
| **Sélection de persona**            | Adaptation du ton et du style de réponse (Avocat, Juge, Étudiant, Citoyen).                    |
| **Prompts d'exemple**              | Liste de questions types liées au droit, chargées depuis `prompts.json`.                      |
| **Historique des conversations**   | Accès aux précédentes discussions et évaluations.                                               |
| **Affichage du raisonnement**       | Option pour afficher le processus de réflexion interne (nœuds LangGraph, étapes de recherche). |
| **Réponse en streaming**            | Affichage des réponses en temps réel.                                                          |
| **Évaluation des réponses**         | Bouton pour évaluer la qualité des réponses (note + justification).                            |

---

## 🛠 **Installation**

### 1. Cloner le dépôt
```bash
git clone https://github.com/votre-utilisateur/code_civil_poc.git
cd code_civil_poc
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Préparer les données
- **Indexer le Code civil** : Utilisez FAISS ou Chroma pour créer un index vectoriel des articles du Code civil.
- **Personnaliser les fichiers JSON** :
  - `personas.json` : Ajoutez/modifiez les personas juridiques.
  - `prompts.json` : Ajoutez des exemples de questions.

---

## 🚀 **Utilisation**

### Lancer l'application
```bash
chainlit run app.py
```
- L'application sera accessible à l'adresse : [http://localhost:8000](http://localhost:8000).

### Interface Utilisateur
1. **Sélectionner un modèle RAG** : Choisissez entre `RAG 1` et `RAG 2`.
2. **Choisir un persona** : Sélectionnez un profil (Avocat, Juge, Étudiant, Citoyen).
3. **Poser une question** :
   - Utilisez un prompt d'exemple ou saisissez votre propre question.
4. **Évaluer la réponse** :
   - Cliquez sur "Évaluer la réponse" pour noter et justifier votre évaluation.

---

## 🔍 **Exemples de Questions**
Voici quelques exemples de questions que vous pouvez poser :
- *"Explique l'article 123 du Code civil."*
- *"Quelle est la procédure pour un divorce par consentement mutuel ?"*
- *"Quels sont les droits du locataire en cas de non-respect du bail ?"*

---

## 📊 **Évaluation des Réponses**
Chaque réponse peut être évaluée avec :
- Une **note** (1 à 5).
- Une **justification** (texte libre).

Les évaluations sont enregistrées dans l'historique.

---

## 🔄 **Prochaines Étapes**
- [ ] **Améliorer les modèles RAG** : Ajouter des sources juridiques supplémentaires.
- [ ] **Déployer l'application** : Mettre en production avec Docker ou un service cloud.
- [ ] **Ajouter des tests unitaires** : Valider la robustesse des modèles.
- [ ] **Intégrer une base de données** : Stocker les historiques et évaluations de manière persistante.

---

## 🤝 **Contribuer**
Les contributions sont les bienvenues ! Pour contribuer :
1. Forkez le projet.
2. Créez une branche (`git checkout -b feature/ma-nouvelle-fonctionnalité`).
3. Commitez vos changements (`git commit -m "Ajout d'une nouvelle fonctionnalité"`).
4. Poussez la branche (`git push origin feature/ma-nouvelle-fonctionnalité`).
5. Ouvrez une Pull Request.

---

## 📜 **Licence**
Ce projet est sous licence **MIT**. Voir le fichier `LICENSE` pour plus de détails.

---

## 📬 **Contact**
Pour toute question ou suggestion, contactez-moi à [votre-email@example.com](mailto:votre-email@example.com).