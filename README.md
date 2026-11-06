# ProjectDoc

[English](README.en.md) · Français

ProjectDoc aide Codex et Claude Code à garder une documentation courte et utile au fil du
développement. Il la crée si elle manque et actualise les explications concernées
si elle existe déjà. Une personne qui découvre ou reprend le projet doit pouvoir
comprendre son but et commencer sans lire tout le code.

ProjectDoc est disponible pour Codex et Claude Code depuis le dépôt GitHub privé
[masskrdjn/projectdoc](https://github.com/masskrdjn/projectdoc).
Voir [l'installation dans Claude Code](#installation-dans-claude-code).

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

## Installation dans Claude Code

Il faut Claude Code, Git avec accès au dépôt privé et Python 3.10 ou plus
accessible via `python`. Après publication de la variante Claude Code sur GitHub,
exécuter ces commandes depuis un terminal :

```powershell
claude plugin marketplace add masskrdjn/projectdoc
claude plugin install projectdoc@projectdoc
```

Dans une session Claude Code, utiliser `/reload-plugins` pour charger le plugin
et `/hooks` pour vérifier que ProjectDoc fournit les deux contrôles. Pour lancer
une revue documentaire à la demande, utiliser `/projectdoc:maintain-project-docs`.

## Pendant une tâche

1. Codex reçoit les consignes et repère la documentation avant de développer.
2. Il réalise le changement, puis crée ou actualise les explications nécessaires.
3. Un contrôle compare les fichiers au début et à la fin. Si le projet a changé
   sans changement documentaire, il demande une vérification supplémentaire.

Vous pouvez parler à Codex en français ou en anglais sans changer de réglage.
Codex répond dans la langue de votre demande. Il conserve la langue des documents
existants, sauf consigne contraire. Si le projet n'a pas de documentation, il
utilise la langue de votre demande, ou l'anglais si elle est indéterminée. Les
libellés techniques du plugin sont en anglais.

Une correction interne peut laisser les documents parfaitement exacts : Codex
explique alors brièvement qu'aucune mise à jour n'est nécessaire. Le contrôle
ne demande qu'une seule reprise par tâche, pour éviter une boucle.

Pour une revue documentaire autonome, invoquez le skill
`maintain-project-docs` dans Codex. Sans périmètre indiqué, il examine le projet
entier si celui-ci est dépourvu de documentation et crée son README. Si une documentation
existe, il examine les changements Git en cours et rend compte de chaque
chantier. Avec un arbre Git propre, il vérifie le parcours de prise en main
et lit un échantillon des pages techniques lorsqu'elles existent. Nommez un
chantier ou un fichier pour limiter la revue.

Si aucune vérification n'apparaît, consultez **Réglages > Hooks** dans Codex,
puis suivez le [diagnostic des hooks](docs/maintenance.md#diagnostiquer-les-hooks).

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
