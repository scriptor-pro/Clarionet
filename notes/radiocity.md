# Radiocity — Notes de fabrication

Radiocity est né d’un besoin simple : écouter des radios en ligne sans lourdeur, sans compte, sans dépendances cloud. L’idée a été de construire un lecteur minimaliste, rapide et prévisible, qui s’efface derrière l’usage.

## Intention

Le projet suit une ligne claire : pas de forme sans fonction, pas d’accumulation. Une seule fenêtre, des actions évidentes, des données locales et lisibles. Le but est de rendre l’écoute aussi immédiate que l’allumage d’un vieux poste.

## Choix techniques

- **Python 3** pour la rapidité d’itération et la clarté du code.
- **GTK3 + PyGObject** pour une interface native sur Linux.
- **mpv** pour la lecture audio, via son socket IPC JSON.

Ces choix privilégient la robustesse et l’intégration système plutôt que l’effet “app web”.

## Architecture simple

Le cœur tient dans un seul fichier : `radiocity.py`. C’est une contrainte volontaire qui rend l’application facile à parcourir et à modifier. Les données (radios, config, logs) vivent dans `~/.config/radiocity/` pour rester locales et transparentes.

## Interaction et états

L’application écoute les événements mpv (idle, loading, playing, paused) pour afficher l’état courant. Les raccourcis clavier suivent la logique d’un lecteur physique : espace pour lecture/pause, S pour stop, flèches pour le volume et la navigation.

## Design et ambiance

Le style visuel cherche la sobriété : une grille simple, une typographie lisible, et un affichage “digital” pour le now‑playing. Le fond brossé et le vert LED rappellent l’univers des équipements audio classiques sans tomber dans le rétro gratuit.

## Ce que Radiocity ne veut pas être

Pas de comptes, pas de recommandations, pas de tracking. Radiocity reste un outil local, discret et stable. Cette contrainte est autant un choix éthique qu’une manière de garder l’application légère.

## À faire évoluer (peut‑être)

- Meilleure accessibilité clavier
- Packaging propre (desktop entry + icône)
- Option de migration vers Rust à long terme

---

Ce document sert de point d’ancrage : pourquoi l’application existe, et quelle simplicité elle doit préserver.