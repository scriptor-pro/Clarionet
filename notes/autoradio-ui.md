# Clarionet — draft UI autoradio

## Objectif

Reprendre les codes d’un autoradio physique : une zone d’affichage centrale, des commandes larges, peu d’éléments simultanés, et des actions évidentes.

## Structure proposée

```
[ Top bar ]  Icône | État | (menu minimal)

[ Presets ]  1  2  3  4  5  6

[ Display ]  NOM STATION (LED)
             Artiste – Titre (LED)

[ Controls ]  ◀︎  ▶︎  Play/Pause  Stop

[ Volume ]    🔊  valeur  −  +
```

## Principes UI

- **Affichage central** : grande zone LCD/LED contrastée (fond sombre, texte vert/ambre).
- **Presets** : 6 boutons persistants, appui long pour enregistrer la station en cours.
- **Navigation** : flèches grandes pour station précédente/suivante (appui long = défilement rapide).
- **Lecture** : bouton unique Play/Pause (évite doublons visuels).
- **Volume** : affichage numérique + pas fin, répétition au maintien du clic.

## Hiérarchie visuelle

1. Affichage station/titre (zone principale)
2. Presets
3. Commandes lecture/navigation
4. Volume

## CSS suggéré (ambiance)

- Fond général sombre, texture légère.
- Boutons carrés type matériel, bordure nette.
- Police digitale pour l’affichage principal et la sélection de station.
- Labels secondaires en blanc cassé.

---

Ce draft sert de base pour itérer sans perdre l’état actuel.