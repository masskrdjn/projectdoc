# Changements

## 0.6.1 — 21 novembre 2026

- Les guides de maintenance décrivent la convention de tags Git annotés
  `vX.Y.Z` pour les publications de ProjectDoc.

## 0.6.0 — 21 novembre 2026

- Ajout d'un hook Antigravity `SessionStart` (`hooks/check_update.py` dans `hooks.json`)
  qui vérifie en lecture seule les mises à jour du plugin sur `main` avec un cache TTL
  de 2 heures (7 200 s) dans `PLUGIN_DATA/update-check.json` (ou le dossier temporaire
  `antigravity-projectdoc/update-check.json`).
- Lorsqu'une version plus récente est disponible, un avis Markdown discret
  (`metadata.user_markdown`) s'affiche au démarrage de la session sans solliciter le
  modèle. Désactivable via `PROJECTDOC_NO_UPDATE_CHECK=1`.
- Ajout des tests unitaires dédiés (`tests/test_check_update.py`) et mise à jour des
  guides français et anglais.

## 0.5.0 — 21 novembre 2026

- Prise en charge native de Google Antigravity avec `.antigravity-plugin/plugin.json`,
  `hooks.json` à la racine et le mode `--antigravity` dans `hooks/documentation.py`
  (`PreInvocation` avec préservation de la baseline en cours de tour, `Stop` avec
  `decision: "continue"`, `continuationActive` et nettoyage sur arrêt anormal).
- Exclusion de `GEMINI.md` de la détection des documents lecteur.
- Ajout des tests unitaires Antigravity et mise à jour des guides français et anglais.

## 0.4.1 — 6 novembre 2026

- Les guides de maintenance indiquent les deux manifestes à mettre à jour
  avant livraison et décrivent le même scénario de vérification dans Codex.

## 0.4.0 — 6 novembre 2026

- Sur un dépôt documenté et propre, la revue autonome vérifie le parcours de
  reprise technique. Elle lit des pages représentatives, distingue guides
  actuels et rapports datés et explique où intervenir ou pourquoi conserver
  la documentation telle quelle.

## 0.3.0 — 5 novembre 2026

- Ajout du plugin Claude Code et de son catalogue dans le même dépôt. Le skill
  et le contrôle documentaire sont partagés. Claude Code remplace son état de
  référence à chaque demande dans la session.

## 0.2.3 — 5 novembre 2026

- Sur un projet sans documentation, une revue autonome sans périmètre explicite
  couvre le projet entier et crée son README, même si des changements Git sont
  en cours.

## 0.2.2 — 5 novembre 2026

- Une revue documentaire autonome sans périmètre explicite couvre tous les
  changements en cours, y compris les fichiers non suivis et non ignorés.
- Le bilan rend compte de chaque chantier examiné. Le rappel de fin de tour
  conserve son périmètre : les changements intervenus pendant le tour.

## 0.2.1 — 5 novembre 2026

- Déplacement du manifeste vers `.codex-plugin/plugin.json` pour que Codex
  charge les hooks ProjectDoc et les propose à l'approbation.

- Avertissements distincts pour un champ manquant, un état initial introuvable
  et un contrôle indisponible.
- Traces facultatives des décisions dans Codex, sans données du projet ni
  identifiants, et test de reprise après modification d'un fichier `.txt`.

## 0.2.0 — 5 novembre 2026

- Prise en charge de l'anglais sans sélection manuelle : réponses dans la langue
  de l'utilisateur et respect de celle des documents existants.
- Instructions internes et fiche du plugin en anglais ; guides anglais et français.
- Vérifications en français, en anglais et sur un projet de langue différente.

## 0.1.1 — 5 novembre 2026

- Installation depuis la marketplace du dépôt GitHub privé.
- Consignes de code et incrément obligatoire de version dans AGENTS.md.
- Ajout de ce suivi des versions.

## 0.1.0 — 5 novembre 2026

- Création du plugin Codex, de ses règles de rédaction et de ses deux hooks.
- Documentation concise, navigation et schémas Mermaid ou SVG selon le besoin.
- Contrôle documentaire avec une seule demande de reprise par tâche.
