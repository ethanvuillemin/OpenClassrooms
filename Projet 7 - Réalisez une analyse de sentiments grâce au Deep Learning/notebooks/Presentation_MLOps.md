# Présentation synthétique des principes du MLOps et de ses apports
## Qu'est-ce que le MLOps ?
Le MLOps (Machine Learning Operations) est une méthodologie qui combine les pratiques du développement logiciel (DevOps) avec la gestion des modèles d'apprentissage automatique (Machine Learning). Son objectif principal est d'automatiser, de standardiser et de rendre reproductible le cycle de vie des modèles ML, depuis leur conception jusqu'à leur déploiement en production et leur maintenance continue.

![alt text](https://ensae-reproductibilite.github.io/website/mlops.png)

## Les principes fondamentaux du MLOps

**1. Automatisation des pipelines**
Le MLOps repose sur l'automatisation des processus clés : préparation des données, entraînement des modèles, validation, déploiement et surveillance. Cela réduit les erreurs humaines et accélère le temps de mise en production.
Reproductibilité
Toutes les étapes du pipeline doivent être traçables et reproductibles. Cela inclut la version des données, des modèles, des hyperparamètres et du code source. Les outils comme Git, Docker ou MLflow sont couramment utilisés pour garantir cette traçabilité.

**2. Collaboration entre équipes**
Le MLOps favorise la collaboration entre les data scientists, les ingénieurs DevOps, les experts métier et les équipes IT. Cette approche multidisciplinaire permet de combler les écarts entre la recherche et la production.
Surveillance continue
Une fois déployés, les modèles doivent être surveillés pour détecter toute dérive (data drift, concept drift) ou baisse de performance. Des métriques clés comme la précision, le rappel ou le F1-score sont suivies en temps réel.
Itération rapide et mise à jour des modèles
Les modèles ML ne sont pas statiques. Le MLOps encourage une approche itérative où les modèles sont régulièrement mis à jour pour refléter les nouvelles données et les évolutions du contexte métier.

**3. Scalabilité et robustesse**
Les solutions MLOps sont conçues pour fonctionner à grande échelle, gérer des volumes massifs de données et s'adapter aux fluctuations de charge dans un environnement de production.

## Les apports du MLOps

**2. Réduction des coûts opérationnels**
En automatisant les tâches répétitives et en minimisant les erreurs humaines, le MLOps optimise les ressources et réduit les coûts liés à la maintenance.
Alignement avec les objectifs métiers
Le MLOps garantit que les modèles ML répondent aux besoins spécifiques des parties prenantes métier, en intégrant des métriques et des KPI alignés sur les objectifs organisationnels.

**3. Gestion des risques** 
En assurant une traçabilité complète et une gouvernance stricte, le MLOps aide à répondre aux exigences réglementaires et à minimiser les risques liés aux biais algorithmiques ou aux violations de données.

**4. Adaptabilité face aux changements**
Les pipelines MLOps permettent de rapidement ajuster les modèles en fonction des évolutions des données ou des besoins métiers, garantissant ainsi leur pertinence à long terme.

# Conclusion
Le MLOps est devenu un pilier essentiel pour toute organisation cherchant à industrialiser ses projets d'intelligence artificielle. En combinant automatisation, collaboration et surveillance continue, il permet non seulement de déployer des modèles ML plus rapidement et de manière plus fiable, mais aussi de maximiser leur valeur ajoutée pour l'entreprise.


# Comparaison des trois approches de modèles ML

Comparaison des trois approches de modélisation
Dans le cadre de notre projet de classification textuelle (par exemple, détection de sentiments ou catégorisation de documents), nous avons mis en œuvre trois approches différentes de modèles d’apprentissage automatique et d’apprentissage profond. Chacune a ses forces, ses faiblesses, et son niveau de complexité, ce qui influence directement la démarche MLOps à adopter.

## 1. Modèle sur mesure simple : Régression logistique
La régression logistique est un modèle statistique utilisé pour les problèmes de classification binaire ou multi-classes. Elle s’applique ici après vectorisation des textes via une méthode comme TF-IDF ou Bag-of-Words.


## 2. Modèle sur mesure avancé : LSTM bidirectionnel
Un réseau LSTM (Long Short-Term Memory) est un type de réseau de neurones récurrent (RNN) capable de capturer les séquences temporelles dans les données. Un LSTM bidirectionnel combine deux réseaux LSTM : l’un lisant la séquence dans l’ordre normal, l’autre dans l’ordre inverse, ce qui permet de capturer mieux le contexte autour de chaque mot.


## 3. Modèle avancé BERT : BERT-base uncased
BERT (Bidirectional Encoder Representations from Transformers) est un modèle pré-entraîné basé sur l’architecture Transformer, développé par Google. Il est capable de comprendre le sens des mots en fonction de leur contexte dans une phrase entière. Nous utilisons ici BERT-base uncased , version simplifiée du modèle avec 12 couches d’encodeurs, 768 dimensions d’embedding et 12 têtes d’attention.


| Critère                    | Régression logistique | LSTM bidirectionnel | BERT-base uncased |
|----------------------------|-----------------------|----------------------|-------------------|
| **Type de modèle**         | Linéaire              | Récurent (RNN)       | Transformer       |
| **Interprétabilité**       | ✅ Haute              | ⚠️ Moyenne           | ❌ Faible          |
| **Performance sur texte simple** | ✅ Bonne           | ✅ Bonne              | ✅ Excellente      |
| **Performance sur texte complexe** | ❌ Faible        | ✅ Bonne              | ✅ Excellente      |
| **Besoin en données**      | Faible                | Moyen                | Élevé             |
| **Temps d’entraînement**   | ✅ Rapide              | ⚠️ Moyen              | ❌ Lent            |
| **Coût de déploiement**    | ✅ Faible              | ⚠️ Modéré             | ❌ Élevé           |
| **Complexité MLOps**       | ✅ Simple              | ⚠️ Modérée            | ❌ Complexe        |

---


# Implémentation d’un pipeline MLOps complet

Dans le cadre de ce projet, une démarche d’implémentation MLOps a été adoptée afin de garantir la **reproductibilité**, la **traçabilité**, la **qualité** et la **maintenabilité** des modèles tout au long de leur cycle de vie. Cette approche s’est appuyée sur une automatisation poussée des étapes clés du développement et du déploiement, depuis l’entraînement initial jusqu’à la mise en production et la surveillance continue.

Chaque type de modèle — le *modèle sur mesure simple*, le *modèle sur mesure avancé* et le *modèle BERT* — a fait l’objet d’une expérience distincte, permettant de simplifier l’analyse comparative et d’assurer une meilleure lisibilité des résultats. Cela a facilité l’identification des forces et faiblesses respectives de chaque architecture, tant en termes de performance que de complexité opérationnelle.

## Suivi des expériences et gestion des versions avec MLflow

Pour assurer une traçabilité complète des différentes phases d’entraînement, l’outil **MLflow** a été utilisé comme système central de *tracking*. Chaque exécution d’entraînement a été enregistrée sous forme d’une expérience séparée, avec un suivi précis des paramètres utilisés, des métriques obtenues (comme la précision, le F1-score ou encore le temps d’exécution), ainsi que des artefacts générés (modèles, rapports, fichiers de configuration).

Le **Model Registry** de MLflow a également permis de versionner les modèles selon leur niveau de maturité. Cette fonctionnalité a joué un rôle crucial dans la validation préalable au déploiement, notamment pour s’assurer que seul le meilleur modèle validé était pour la production.


## Tests unitaires avec pytest : vérification de la robustesse de l’API

Avant toute mise en production, il est essentiel de valider la stabilité de l’interface API exposée par le modèle. Pour cela, un ensemble de tests unitaires a été mis en place à l’aide de **pytest**. Ces tests couvrent les cas d’entrée typiques, les formats attendus, les erreurs possibles, ainsi que les comportements limites.

Par exemple, des tests spécifiques ont été écrits pour vérifier que :
- Une requête correcte retourne bien une prédiction au format attendu,
- Une donnée mal formée génère une erreur explicite sans planter le service,
- Le modèle répond dans un délai raisonnable, même sous charge légère.

Ces contrôles automatiques, exécutés à chaque push sur la branche principale, constituent une première barrière contre les défaillances fonctionnelles ou logiques avant le déploiement.

## Déploiement de l'api automatisé sur un VPS Hostinger via GitHub Actions

Une fois les tests réussis, le déploiement des modèles a été automatisé grâce à **GitHub Actions**. Un workflow a été configuré pour détecter les nouveaux commits sur la branche principale et déployer sur un serveur VPS fourni par  mes soins depuis la platforme **Hostinger**.

Ce processus combine simplicité et efficacité : GitHub Actions permet de gérer tout le cycle CI/CD sans nécessiter d’infrastructure externe coûteuse. Grâce à cette chaîne automatisée, chaque amélioration du modèle peut être rapidement testée, validée et mise en production, sans intervention manuelle.

## Surveillance en production avec Azure Application Insights

Une fois en production, la supervision active du modèle devient indispensable. Pour cela, **Azure Application Insights** a été intégré à l’API, permettant de collecter des données en temps réel sur les requêtes traitées, les temps de réponse, les erreurs rencontrées, ainsi que les métriques de performance globales.

Des dashboards personnalisés ont été configurés pour visualiser :
- La fréquence des requêtes et leur répartition horaire,
- Les taux d’erreur ou de succès,
- Des declenchements d'alerte si plus de trois appel a l'api sont Négatifs dans les 5min consecutive


