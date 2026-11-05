# Reprendre ProjectDoc

[Retour à l'accueil](../README.md)

Le plugin associe un skill, qui explique à Codex comment rédiger, et des hooks,
de petits programmes lancés pour rappeler les consignes et contrôler les oublis.

## Où intervenir

| Fichier | Rôle |
| --- | --- |
| `plugin.json` | Nom, version et composants du plugin. |
| `.agents/plugins/marketplace.json` | Catalogue fourni par le dépôt GitHub. |
| `AGENTS.md` | Consignes de code, de documentation et de version. |
| `CHANGELOG.md` | Changements de chaque version. |
| `skills/maintain-project-docs/SKILL.md` | Règles de rédaction et de rangement. |
| `hooks/hooks.json` | Moments où Codex lance le contrôle. |
| `hooks/documentation.py` | Comparaison des fichiers et demande de vérification. |
| `tests/test_documentation.py` | Vérifications du comportement des hooks. |

## Fonctionnement

Au début d'une demande (`UserPromptSubmit`), le programme garde une empreinte des
fichiers : une valeur calculée qui change si le contenu change. Il donne aussi à
Codex le chemin du skill à appliquer.

Avant la fin de la réponse (`Stop`), il compare ces empreintes. Un ajout, une
modification ou une suppression hors documentation entraîne une demande de
vérification si les documents sont inchangés ou absents. Un document vide ou un
dessin seul ne suffit pas. Si les documents ont changé et qu'un document lisible
existe, le contrôle laisse terminer.

Il ne demande qu'une reprise par tour, grâce au signal `stop_hook_active` de
Codex et à une trace enregistrée de sa demande. La comparaison ne prouve pas
la justesse des explications : leur relecture reste nécessaire.

## Périmètre et limites

- Dans Git, le contrôle couvre les fichiers suivis et les nouveaux fichiers non
  ignorés, depuis la racine du dépôt. Les modifications antérieures à la demande
  ne sont pas attribuées à cette tâche. Un sous-module se traite séparément.
- Sans Git, il couvre le dossier de travail et ses sous-dossiers, en écartant
  certains dossiers de dépendances et de cache. Utiliser la racine du projet.
  Les liens de fichiers et de dossiers ne sont pas suivis.
- Il reconnaît les documents `.md`, `.mdx`, `.rst`, `.adoc` et les fichiers sous
  `docs/`, `doc/`, `documentation/`, `guide/`, `guides/` ou `handbook/`.
  Les fichiers `AGENTS.md`, `AGENTS.override.md`, `SKILL.md` et les ressources
  sous les dossiers cachés ou `skills/` ne comptent pas comme documentation.
- Un autre emplacement reste utilisable par le skill. Le contrôle peut alors
  demander une vérification supplémentaire sans nécessité de modifier les pages.
- Chaque comparaison est limitée à 15 000 fichiers et 128 Mio. Les appels Git
  ont un délai maximal de 8 secondes et chaque hook de 20 secondes. Une erreur,
  un état initial absent ou un projet trop grand produit un avertissement :
  Codex doit alors vérifier les documents lui-même.
- Les changements simultanés d'un autre outil peuvent apparaître dans la
  comparaison. Les changements hors tâche Codex ne déclenchent rien à eux seuls.

Le programme ne modifie pas les sources, ne lit pas les conversations, ne contacte
aucun service et n'appelle aucun modèle. Codex rédige à partir du projet réel.

L'état est isolé par projet, session et tâche dans `PLUGIN_DATA/turns/`, ou dans
le dossier temporaire `codex-projectdoc/turns/` si `PLUGIN_DATA` manque. Il contient
les noms de fichiers, leurs empreintes et l'heure de création, sans leur contenu.
Ces états peuvent être supprimés après la fin des tâches concernées.

## Vérification d'une évolution

Lancer `python -m unittest discover -s tests -v`. Les tests utilisent des projets
temporaires pour vérifier la création nécessaire, la mise à jour, les suppressions,
les tâches sans changement, la reprise bornée et la comparaison dans Git.

La version 0.1.0 a passé ces 16 tests et une installation par les commandes Codex
dans une configuration isolée. Le chargement et le déroulement complet des hooks
dans l'application restent à vérifier après leur approbation.

Pour vérifier dans l'application, installer le plugin depuis la marketplace
GitHub comme indiqué dans le README et approuver les hooks.
Dans un projet jetable, demander une fonction : Codex doit créer le README.
Changer ensuite son utilisation : le document doit être actualisé. Une simple
demande d'explication ne doit créer aucun fichier. Les tests Python ne remplacent
pas cette validation après installation dans Codex.

Avant chaque livraison, incrémenter la version de `plugin.json` et décrire
l'évolution dans `CHANGELOG.md`, selon les règles d'`AGENTS.md`.

Les contrats utilisés viennent des [hooks Codex](https://developers.openai.com/codex/hooks),
du [format des plugins](https://developers.openai.com/plugins/build/plugins) et
des [instructions AGENTS.md](https://developers.openai.com/codex/guides/agents-md),
consultés le 5 novembre 2026.
