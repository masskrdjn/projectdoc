# Reprendre ProjectDoc

[Retour à l'accueil](../README.md) · [English](maintenance.en.md)

Le plugin associe un skill, qui explique à Codex comment rédiger, et des hooks,
de petits programmes lancés pour rappeler les consignes et contrôler les oublis.

## Où intervenir

| Fichier | Rôle |
| --- | --- |
| `.codex-plugin/plugin.json` | Manifeste Codex : nom, version et composants du plugin. |
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

Le hook transmet la même règle de langue au début de la tâche et s'il demande
une reprise. Codex s'appuie sur la conversation et les documents existants ;
le script ne détecte pas la langue, ne conserve pas la demande et n'a pas besoin
d'une préférence de langue dans les réglages.

## Revue documentaire autonome

Si le projet n'a aucune documentation destinée aux lecteurs et que
l'utilisateur ne fixe pas de périmètre, le skill examine le projet entier
et crée un README, même si Git contient des changements en cours.

Si le projet est documenté, le skill examine les changements déjà présents dans
Git : modifications indexées, modifications non indexées et fichiers non
suivis que Git n'ignore pas. Codex identifie les comportements concernés et
explique pour chacun ce qui a été mis à jour ou pourquoi il n'y avait rien à
changer. Si l'utilisateur nomme un chantier, la revue s'y limite.

Le hook `Stop` reste un rappel pour les changements intervenus pendant le
tour. Il ne vérifie pas que les pages modifiées couvrent tous les comportements
concernés.

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

## Diagnostiquer les hooks

Vérifier dans **Réglages > Hooks** que les deux hooks ProjectDoc sont présents et
approuvés. Pour afficher leurs décisions, démarrer Codex avec la variable
d'environnement `PROJECTDOC_DEBUG=1` dans le processus qui le lance.
Les traces s'affichent comme avertissements Codex, sans identifiant, chemin ni
contenu de fichier. Retirer la variable et redémarrer pour les désactiver.

Dans un dépôt jetable, préparer un fichier `.txt` suivi par Git, puis demander à
Codex d'ajouter un espace en fin de ligne sans autre modification. Attendre
`baseline saved` au début et `documentation review requested` à la fin, avec
une seule reprise. Si seul `Stop` signale `no baseline`, vérifier la trace de
début du même tour. Un champ manquant est nommé dans l'avertissement ; l'absence
de toute trace invite à vérifier l'approbation et le lancement de Python.

## Vérification d'une évolution

Lancer `python -m unittest discover -s tests -v`. Les tests utilisent des projets
temporaires pour vérifier la création nécessaire, la mise à jour, les suppressions,
les tâches sans changement, la reprise bornée et la comparaison dans Git.

Avec la version 0.2.1, une installation isolée a confirmé que Codex détecte les
deux hooks. Leur déroulement complet dans l'application reste à vérifier après
leur approbation.

Pour vérifier dans l'application, installer le plugin depuis la marketplace
GitHub comme indiqué dans le README et approuver les hooks.
Dans un projet jetable, demander une fonction : Codex doit créer le README.
Changer ensuite son utilisation : le document doit être actualisé. Une simple
demande d'explication ne doit créer aucun fichier. Les tests Python ne remplacent
pas cette validation après installation dans Codex.

Pour vérifier le périmètre du skill, préparer trois changements indépendants
avant d'ouvrir un nouveau chat : un changement indexé pour les PDF, un
changement non indexé pour les mails et un fichier non suivi pour le classement.
Prévoir une documentation exacte pour les mails et le classement, mais périmée
pour les PDF. Invoquer le skill seul : il doit corriger la doc PDF et rendre
compte des trois chantiers. Répéter sur une copie en demandant une revue limitée
aux PDF : seuls les PDF doivent entrer dans le bilan.

Pour vérifier les langues dans Codex, demander le même développement en anglais
et en français dans deux projets sans documentation. Vérifier la langue de
chaque réponse et de chaque README. Dans un projet documenté en français,
faire une demande en anglais : la réponse doit être en anglais et la mise à
jour documentaire en français.

Avant chaque livraison, incrémenter la version du manifeste et décrire
l'évolution dans `CHANGELOG.md`, selon les règles d'`AGENTS.md`.

Les contrats utilisés viennent des [hooks Codex](https://developers.openai.com/codex/hooks),
du [format des plugins](https://developers.openai.com/plugins/build/plugins) et
des [instructions AGENTS.md](https://developers.openai.com/codex/guides/agents-md),
consultés le 5 novembre 2026.
