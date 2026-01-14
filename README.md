# Radiocity

Application Linux minimaliste pour ecouter des radios en ligne via GTK3 + mpv.

## Lancer

```bash
python3 radiocity.py
```

## Dependances

- Python 3
- GTK3 + PyGObject
- mpv

## Version

0.1.7

## Donnees

Les fichiers sont stockes dans `~/.config/radiocity/` :

- `radios.json` (id, name, stream_url)
- `config.json` (volume, last_radio_id)
- `radiocity.log`

## Raccourcis

- Lecture: `Espace`
- Arret: `S`
- Volume: `Flèche gauche` / `Flèche droite`
- Radio precedente/suivante: `Flèche haut` / `Flèche bas`
- Ajouter une radio: `Ctrl+N`
- Quitter: `Ctrl+Q`

## Licence

MIT
