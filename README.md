# ProjectDoc

ProjectDoc aide Codex à garder une documentation courte et utile au fil du
développement. Il la crée si elle manque et actualise les explications concernées
si elle existe déjà. Une personne qui découvre ou reprend le projet doit pouvoir
comprendre son but et commencer sans lire tout le code.

Ce plugin cible uniquement Codex. Son installation se fait depuis le dépôt
GitHub privé [masskrdjn/projectdoc](https://github.com/masskrdjn/projectdoc).

## Installation dans Codex

Il faut Codex desktop avec la prise en charge des plugins et des hooks, ainsi que
Python 3.10 ou plus, accessible avec la commande `python`, et Git.
Le compte GitHub utilisé par Git doit avoir accès au dépôt privé. Si nécessaire,
configurer cette connexion avant l'installation ; ne jamais mettre de jeton
d'accès dans les commandes ou les fichiers du projet.

Depuis n'importe quel dossier, ajouter la marketplace hébergée sur GitHub,
puis installer le plugin :

```powershell
codex plugin marketplace add https://github.com/masskrdjn/projectdoc.git --ref main
codex plugin add projectdoc@projectdoc
```

Redémarrer Codex, ouvrir le répertoire des plugins et vérifier que **ProjectDoc**
est activé. Examiner et approuver ses deux hooks
(les actions exécutées au début et à la fin d'une tâche). Sans cette approbation,
le contrôle automatique ne fonctionne pas. Commencer ensuite une nouvelle tâche
dans le projet à développer.

La procédure suit le [guide officiel des plugins Codex](https://developers.openai.com/plugins/build/plugins).
Le plugin installé est une copie du dépôt : après une nouvelle version, mettre
à jour la marketplace et le plugin par le gestionnaire de plugins, redémarrer
Codex et approuver à nouveau les hooks si leur contenu a changé.

## Pendant une tâche

1. Codex reçoit les consignes et repère la documentation avant de développer.
2. Il réalise le changement, puis crée ou actualise les explications nécessaires.
3. Un contrôle compare les fichiers au début et à la fin. Si le projet a changé
   sans changement documentaire, il demande une vérification supplémentaire.

Une correction interne peut laisser les documents parfaitement exacts : Codex
explique alors brièvement qu'aucune mise à jour n'est nécessaire. Le contrôle
ne demande qu'une seule reprise par tâche, pour éviter une boucle.

Les règles sont aussi disponibles par invocation explicite du skill
`maintain-project-docs` dans Codex.

## Où trouver les documents des projets

ProjectDoc respecte les emplacements existants. Pour un nouveau projet :

| Emplacement | Ce qu'on y trouve |
| --- | --- |
| `README.md` | À quoi sert le projet, comment commencer et où poursuivre. |
| `docs/` | Les explications qui méritent une page séparée, si nécessaire. |
| `docs/assets/` | Les schémas SVG, si nécessaire. |
| `AGENTS.md` et `.agents/` | Les consignes et ressources de Codex. |

Chaque page doit être accessible depuis l'accueil. Les schémas Mermaid ou SVG
restent facultatifs : on les ajoute s'ils facilitent la compréhension, avec une
courte explication en texte. Pas de jargon inexpliqué ni de pages de remplissage.

## Reprendre le développement du plugin

Lire [le guide de maintenance](docs/maintenance.md) pour son fonctionnement et ses
limites. Depuis ce dossier, lancer les tests sans installer de bibliothèque :

```powershell
python -m unittest discover -s tests -v
```
