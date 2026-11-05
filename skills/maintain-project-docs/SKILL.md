---
name: maintain-project-docs
description: Create or update concise project documentation when implementing features, fixing bugs, or changing setup, configuration, interfaces or architecture. Also use for project documentation and handover requests.
---

# Documentation accessible

Le lecteur découvre le projet ou le reprend après une absence. Il doit comprendre
à quoi il sert, pouvoir commencer et trouver où poursuivre sans lire le code.
Respecter la langue des documents existants ; pour un projet neuf, utiliser celle
de l'utilisateur. Écrire directement, en phrases courtes et en mots courants.
Expliquer un terme technique nécessaire à sa première apparition. Ne pas produire
de remplissage, de catalogue des fichiers ni de récit de la session.

## Avant et après le développement

Avant de modifier le projet, repérer son point d'entrée documentaire et lire les
pages concernées. Respecter ses instructions et ses choix d'organisation. Après
le développement, confronter les documents au comportement livré et aux commandes
effectivement vérifiées. Mettre à jour les seules explications affectées : usage,
installation, réglages, interfaces, fonctionnement ou reprise du projet.

Si la documentation est absente, créer un README.md à la racine, même si le premier
changement est petit. S'appuyer sur le code et les vérifications disponibles ;
signaler les informations inconnues utiles, sans inventer une procédure qui marche.
Une correction interne sans effet sur les explications existantes peut ne demander
aucune modification documentaire : le signaler brièvement en fin de tâche.
Ne pas modifier une documentation à jour uniquement pour satisfaire le contrôle.

## Placement et navigation

- Conserver les emplacements existants, y compris un site documentaire ou un dossier
  au nom différent. Ne pas créer une deuxième source de vérité et ne pas déplacer
  les pages sans nécessité.
- Par défaut, placer l'accueil dans README.md : but du projet, démarrage rapide,
  liens vers les explications utiles. Garder un projet simple sur cette seule page.
- Utiliser docs/ quand un sujet mérite sa propre page. Chaque page doit être
  accessible depuis le README, directement ou par un index, et proposer un retour
  vers l'accueil. Préférer des liens relatifs versionnés avec le code.
- Réserver AGENTS.md aux consignes de travail de Codex. .agents/ héberge les
  ressources des agents ; ce n'est pas l'accueil documentaire des personnes.
- Pour la reprise, indiquer les quelques commandes, réglages et dépendances
  indispensables. Ajouter les décisions et limites utiles à la maintenance
  seulement lorsqu'elles ne se déduisent pas des explications existantes.

## Schémas utiles

Ajouter un schéma s'il rend un parcours, des relations ou une circulation de
données plus faciles à comprendre que quelques phrases. Ne pas en ajouter par
principe. Employer des libellés courants, peu d'éléments et une légende si utile.

Choisir Mermaid pour un schéma simple facile à modifier en texte, si le support
de lecture sait l'afficher. Préférer un SVG local si un rendu précis, un export
ou un lecteur sans Mermaid le justifie. Ranger le SVG dans docs/assets/ (ou le
dossier équivalent existant), l'intégrer avec un texte alternatif descriptif,
sans script, contenu distant ni ressource externe nécessaire au rendu.
Dans les deux cas, conserver une courte explication textuelle compréhensible
sans le dessin. Éviter deux versions manuellement synchronisées du même schéma.

## Vérification finale

Relire avec le regard d'une personne nouvelle : le but, le premier pas et la
navigation sont-ils évidents ? Les exemples correspondent-ils au changement ?
Vérifier les liens relatifs et les commandes concernées lorsque l'environnement
le permet. Utiliser le moteur de rendu existant pour les schémas, s'il est
disponible ; sinon indiquer que leur rendu n'a pas été vérifié.
Ne jamais copier de secrets ou de données personnelles depuis le code ou les
réglages. Ne pas publier les documents ni modifier des droits de partage.

Le hook fournit un rappel et un contrôle des changements de fichiers. Il ne
juge pas la justesse du texte. Si le contrôle demande une reprise, effectuer
la vérification documentaire puis terminer, en indiquant toute limite réelle.
