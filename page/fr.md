# Clarionet

Clarionet est un lecteur de radios en ligne minimaliste pour Linux. L’objectif est simple : une interface rapide, lisible, et un fonctionnement local sans compte ni services externes.

## Ce que fait l’app

- Lecture de flux radio via mpv (m3u8, mp3, etc.)
- Import de stations manuellement ou via Radio‑Browser
- Presets 1–6 avec appui long pour mémoriser
- Affichage « LED » pour la station et les métadonnées
- Contrôle du volume système

## Philosophie

Clarionet privilégie la sobriété : peu d’éléments visibles, des actions directes, et une interface inspirée des autoradios des années 80. Les données restent locales dans `~/.config/clarionet/`.

## Installation

```bash
./install.sh
```

Puis lancer l’app :

```bash
./clarionet
```

## Raccourcis

- Espace : lecture/pause
- S : stop
- Flèches gauche/droite : volume −/+
- Flèches haut/bas : station précédente/suivante

## Statut

Projet en évolution. Les retours UX et les idées de presets sont bienvenus.
