# Clarionet

Application Linux minimaliste pour ecouter des radios en ligne via GTK3 + mpv.

## Lancer

```bash
./clarionet
```

## Dependances

- Python 3
- GTK3 + PyGObject
- mpv

## Version

87.5.026

## Donnees

Les fichiers sont stockes dans `~/.config/clarionet/` :

- `radios.json` (id, name, stream_url)
- `config.json` (volume, last_radio_id)
- `clarionet.log`

## Raccourcis

- Lecture: `Espace`
- Arret: `S`
- Volume: `Flèche gauche` / `Flèche droite`
- Radio precedente/suivante: `Flèche haut` / `Flèche bas`
- Ajouter une radio: `Ctrl+N`
- Quitter: `Ctrl+Q`

## Licence

MIT
