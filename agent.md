# Radiocity — agent.md

## 1. Identité du projet

**Nom du projet**  
Radiocity

**Statut**  
Usage personnel dans un premier temps, avec objectif de publication.

**Phrase d’intention**  
Radiocity est une application Linux simple et minimaliste permettant d’écouter des radios en ligne.  
Elle privilégie la fonction à la forme, la sobriété à l’accumulation, et l’intégration native au desktop Linux.

---

## 2. Philosophie générale

- Pas de forme sans fonction  
- Simplicité avant sophistication  
- Pas de compte utilisateur  
- Pas de cloud  
- Pas de tracking  
- Données locales, lisibles et modifiables  
- Application discrète, rapide et prévisible  

Radiocity doit s’effacer derrière l’usage : choisir une radio, appuyer sur lecture, écouter.

---

## 3. Périmètre fonctionnel — Version 1 (V1)

### Fonctionnalités incluses

- Affichage d’une liste de radios  
- Lecture d’un stream radio  
- Pause / reprise  
- Arrêt de la lecture  
- Augmenter / diminuer le volume  
- Affichage du nom de la radio en cours  
- Indication de l’état (en lecture / arrêtée)  
- Ajout et suppression de radios via l’interface  
- Persistance de la liste des radios via un fichier `.json`  

### Fonctionnalités explicitement exclues

- Comptes utilisateurs  
- Synchronisation en ligne  
- Visualiseur audio  
- Égaliseur  
- Historique d’écoute avancé  
- Recommandations  
- Streaming local / DLNA  

---

## 4. Radios incluses par défaut

- Radios publiques francophones  
- Radios SomaFM  

Ces radios sont fournies comme valeurs par défaut et peuvent être modifiées ou supprimées par l’utilisateur.

---

## 5. Interface utilisateur (UX / UI)

### Principes UX

- Une seule fenêtre  
- Interface lisible immédiatement  
- Aucun élément décoratif sans fonction  
- Interactions évidentes, sans apprentissage  

### Interface principale

- Liste des radios  
- Boutons : lecture / arrêt  
- Contrôle du volume  
- Affichage du nom de la radio sélectionnée  
- Indicateur d’état de lecture  

---

## 6. Intégration Linux / Desktop

- Fichier `.desktop`  
- Icône personnalisée  
- Raccourcis clavier pour lecture et arrêt  
- Présence dans le tray (zone de notification)  

### Comportement

- La radio peut continuer à jouer lorsque la fenêtre est fermée  
- Quitter explicitement l’application arrête la lecture  

---

## 7. Choix techniques — Version 1

### Langage

- Python 3  
- Choisi pour la rapidité de développement, la lisibilité et l’intégration GTK  
- Migration vers Rust envisagée pour une version 2  

### Interface graphique

- GTK3  
- PyGObject  

### Lecture audio

- mpv  

### Contrôle de mpv

- IPC Socket (JSON)  

---

## 8. Données et configuration

### Emplacement

```
~/.config/radiocity/
```

### Fichiers

- `radios.json`  
- `config.json`  

---

## 9. Distribution et publication

- Dépôt public envisagé (GitHub / Codeberg)  
- Licence libre : MIT  

---

## 10. Ligne rouge

Radiocity ne deviendra pas :
- une usine à fonctionnalités  
- une application web déguisée  
- un produit dépendant d’un service externe  

---

## 11. Évolution envisagée (hors V1)

- Migration possible vers Rust  
- Amélioration de l’accessibilité  
- Raffinement de l’intégration desktop  

---

## 12. Licence

Radiocity est distribué sous licence MIT.

---

## 13. Spécification UI figée (V1)

### Grille

- Grille de base : 8 px  
- Espacements autorisés : 8 / 16 / 24 / 32 / 56 px  

### Structure

- Header : 56 px  
- Corps : liste radios + now playing  
- Footer : 56 px  

---

## 14. Typographie

- Police principale : police système GTK  
- Police secondaire : Inter UI (usage limité)  

Tailles :
- Texte UI : 14 px  
- Labels secondaires : 12 px  
- Titres : 20 px  
- Nom radio : 24 px  

---

## 15. Couleurs

- Thème clair et sombre (système)  
- Couleur d’accent unique : #002fa7  

---

## 16. Raccourcis clavier

- Lecture : Espace  
- Arrêt : S  
- Volume + / - : Flèches droite / gauche  
- Radio suivante / précédente : Flèches bas / haut  
- Ajouter une radio : Ctrl + N  
- Quitter : Ctrl + Q  

---

## 17. États applicatifs

- idle  
- loading  
- playing  
- paused  
- error  

États pilotés exclusivement par mpv.

---

## 18. Journalisation

- Activée par défaut  
- Locale uniquement  
- Fichier : `~/.config/radiocity/radiocity.log`  

---

## 19. Spécification IPC mpv

- Commandes utilisées : loadfile, stop, set pause, set volume  
- Événements écoutés : file-loaded, playback-restart, end-file, error  

---

## 20. Format des fichiers

### radios.json

- Tableau d’objets  
- Champs : id, name, stream_url  

### config.json

- volume (0–100)  
- last_radio_id  

