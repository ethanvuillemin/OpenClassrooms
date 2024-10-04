# Projet 3 - Préparez des données pour un organisme de santé publique

L'agence Santé publique France souhaite **améliorer sa base de données Open Food Facts** et fait appel aux services de votre entreprise. Cette base de données open source est mise à la disposition de particuliers et d’organisations afin de leur permettre de connaître la qualité nutritionnelle de produits.

Acceder au dataset  [ici](https://s3-eu-west-1.amazonaws.com/static.oc-static.com/prod/courses/files/parcours-data-scientist/P2/fr.openfoodfacts.org.products.csv.zip)

<img src="https://triviawhizz.com/wp-content/uploads/2024/05/658361f62354fb75eeba29d6_Food-Food-drink-750x375.jpg" alt="images descriptive du chapitre" style="width: 100%;">


# Contexte du projet - Extrait de mail
    Bonjour, 


    Le jeu de données Open Food Facts est disponible sur le site officiel (ou disponible à ce lien en téléchargement). Les variables sont définies à cette adresse. Les champs sont séparés en quatre sections :

    Les informations générales sur la fiche du produit : nom, date de modification, etc.
    Un ensemble de tags : catégorie du produit, localisation, origine, etc.
    Les ingrédients composant les produits et leurs additifs éventuels
    Des informations nutritionnelles : quantité en grammes d’un nutriment pour 100 grammes du produit
    Afin de simplifier ton approche, je te propose de commencer par établir la faisabilité de suggérer les valeurs manquantes pour une variable dont plus de 50% des valeurs sont manquantes.

    

    Voici les différentes étapes pour nettoyer et explorer les données :

    

    1) Traiter le jeu de données

    Repérer des variables pertinentes pour les traitements à venir, et nécessaires pour suggérer des valeurs manquantes,.
    Nettoyer les données en :
    mettant en évidence les éventuelles valeurs manquantes parmi les variables pertinentes sélectionnées, avec au moins 3 méthodes de traitement adaptées aux variables concernées,
    identifiant et en traitant les éventuelles valeurs aberrantes de chaque variable.
    Automatiser ces traitements pour éviter de répéter ces opérations
    Attention, le client souhaite que le programme fonctionne si la base de données est légèrement modifiée (ajout d’entrées, par exemple) !

    

    2) Tout au long de l’analyse, produire des visualisations afin de mieux comprendre les données. Effectuer une analyse univariée pour chaque variable intéressante, afin de synthétiser son comportement.

    

    Et un mot à ce sujet : le client nous demande de réaliser une présentation qui permet d’expliquer les analyses faites à un public néophyte. Sois donc attentif à la lisibilité : taille des textes, choix des couleurs, netteté suffisante, et variez les graphiques (boxplots, histogrammes, diagrammes circulaires, nuages de points…) pour illustrer au mieux ton propos.

    

    3) Sélectionner / créer des variables à l’aide d’une analyse multivariée. Effectuer les tests statistiques appropriés pour vérifier la significativité des résultats.

    

    4) Rédiger un rapport d’exploration et une conclusion pour expliquer la faisabilité de l’application demandée.

    

    5) Même si les données n’incluent pas de données personnelles, on doit expliquer dans une présentation en quoi ce projet respecte les 5 grands principes du RGPD. Santé publique France aimerait publier quelque chose sur le site Open Food Facts pour couper court aux questions sur le respect des RGPD que nous recevons parfois. 

    Bon courage ! 

    Alma