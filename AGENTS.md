# Développement de ProjectDoc

## Règles de code

- Cibler Codex uniquement et préserver les formats de plugins et de hooks pris
  en charge. Éviter les dépendances externes quand la bibliothèque Python suffit.
- Écrire des fonctions courtes, avec des noms explicites. Commenter les raisons
  et les limites utiles plutôt que paraphraser le code.
- Préserver les fichiers et les changements existants. Ne jamais enregistrer de
  secrets, d'état local ou de fichiers temporaires dans le dépôt.
- Garder les changements limités au besoin et ajouter un test de comportement
  lorsqu'une logique du contrôle change. Vérifier les erreurs et les cas limites.
- Avant livraison, exécuter les tests ci-dessous, vérifier les fichiers JSON et
  les liens documentaires concernés. Signaler les vérifications impossibles.

## Version et livraison

Après chaque développement livré, y compris une évolution des instructions ou
de la documentation, incrémenter la version dans `plugin.json` avant le commit.
Utiliser `MAJEURE.MINEURE.CORRECTIF` : correctif pour une correction ou de la
documentation, mineure pour une fonctionnalité compatible, majeure pour une
rupture de compatibilité. Un lot cohérent de changements reçoit une seule version.
Documenter le résultat dans `CHANGELOG.md` et actualiser les références à la
version lorsqu'elles décrivent la version courante. Ne jamais réutiliser une
version déjà publiée pour un contenu différent.

La branche publiée est `main`. Le dépôt GitHub et son catalogue de plugins
constituent la source d'installation ; le guide doit utiliser cette adresse,
sans dépendre d'un chemin local sur le poste de développement.

## Documentation et garanties

ProjectDoc cible Codex uniquement. La documentation destinée aux personnes commence
dans README.md ; les détails utiles vont dans docs/. À chaque développement,
appliquer skills/maintain-project-docs/SKILL.md : créer la documentation absente ou
actualiser les explications affectées. Rester bref et compréhensible sans connaître
le projet. Les schémas Mermaid ou SVG doivent apporter une aide réelle.

Les hooks ne modifient jamais les sources, n'appellent aucun modèle et n'envoient
aucune donnée sur le réseau. Leur contrôle ne prouve pas la justesse des documents.
Toute continuation demandée par Stop doit être bornée à une fois par tour.

Validation : `python -m unittest discover -s tests -v`.
