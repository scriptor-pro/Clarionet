# Système de Rapport de Plantage Clarionet

## Vue d'ensemble

Clarionet intègre maintenant un système robuste de capture et de rapport des plantages. Cela permet de diagnostiquer et de corriger les bugs de manière efficace.

## Fonctionnement

### 1. Capture automatique des plantages

Lors du démarrage de Clarionet, un gestionnaire d'exceptions global est configuré pour capturer toutes les erreurs non gérées.

- Tous les plantages sont enregistrés dans un fichier JSON structuré
- Les rapports contiennent:
  - L'ID unique du plantage
  - L'horodatage exact
  - Le type et le message d'erreur
  - La pile d'appels complète (traceback)
  - La version de l'application
  - La version de Python et la plateforme

### 2. Notifications au démarrage

À chaque lancement de Clarionet, l'application vérifie les plantages précédents et affiche une notification modale si des rapports sont trouvés. Cela permet au développeur d'être immédiatement informé des problèmes.

### 3. Stockage local

Les rapports de plantage sont stockés dans:
```
~/.config/clarionet/crashes/
```

Chaque rapport a un nom unique:
```
crash_YYYY-MM-DD_HH-MM-SS_XXXXXXXX.json
```

## Utilisation

### Via l'interface graphique

1. Clarionet affiche automatiquement une notification si un plantage s'est produit lors du lancement précédent
2. La notification affiche:
   - Le type d'erreur
   - Le message d'erreur
   - L'heure du plantage
   - L'ID unique du rapport

### Via le script `crash_reporter.py`

#### Lister tous les plantages

```bash
python3 crash_reporter.py list
```

Affiche:
```
📋 3 rapport(s) de plantage trouvé(s):

ID                                                 Type                 Date/Heure
---
crash_2026-04-25_14-30-15_a1b2c3d4                ZeroDivisionError    2026-04-25_14-30-15
crash_2026-04-25_14-35-22_e5f6g7h8                AttributeError       2026-04-25_14-35-22
crash_2026-04-25_14-40-45_i9j0k1l2                ValueError           2026-04-25_14-40-45
```

#### Afficher les détails d'un plantage

```bash
python3 crash_reporter.py show 2026-04-25_14-30-15
```

Affiche le rapport complet avec:
- L'identifiant du plantage
- La date et l'heure
- Le type et le message d'erreur
- La pile d'appels complète
- Les informations sur l'environnement

Exemple:

```
================================================================================
📄 RAPPORT DE PLANTAGE
================================================================================

🔍 Identifiant: crash_2026-04-25_14-30-15_a1b2c3d4
📅 Date/Heure: 2026-04-25_14-30-15
📱 Application: Clarionet v87.5.028

⚠️  EXCEPTION
--------------------------------------------------------------------------------
Type: ZeroDivisionError
Message: division by zero

🐍 TRACEBACK
--------------------------------------------------------------------------------
Traceback (most recent call last):
  File "clarionet.py", line 1234, in play_stream
    volume = 100 / 0
ZeroDivisionError: division by zero

💻 ENVIRONNEMENT
--------------------------------------------------------------------------------
Python: 3.11.2 (main, Feb 17 2024, 00:00:00) 
Plateforme: linux
================================================================================
```

#### Supprimer les plantages

Supprimer un plantage spécifique:
```bash
python3 crash_reporter.py delete 2026-04-25_14-30-15
```

Supprimer tous les plantages:
```bash
python3 crash_reporter.py delete --all
```

## Architecture technique

### Fichier `clarionet.py`

Nouvelles fonctions et modificaations:

#### Fonction `create_crash_report(exc_type, exc_value, tb)`

Crée un fichier JSON structuré contenant tous les détails d'un plantage.

- Paramètres:
  - `exc_type`: Type de l'exception
  - `exc_value`: Valeur/message de l'exception
  - `tb`: Trace de pile (traceback)

- Retourne: `(crash_id, crash_file)`

#### Fonction `setup_crash_handler()`

Configure le gestionnaire global d'exceptions. Doit être appelée au démarrage de l'application.

- Intercepte `sys.excepthook`
- Ignore les `KeyboardInterrupt` (Ctrl+C)
- Enregistre les exceptions critiques
- Appelle `create_crash_report` pour chaque plantage

#### Fonction `check_for_pending_crash_reports(window)`

Vérifie la présence de plantages précédents au démarrage.

- Paramètre: `window` (la fenêtre principale Gtk)
- Affiche une notification modale pour les 5 plantages les plus récents
- Enregistre l'acknowledgement des rapports

#### Méthode `ClarionetApp.report_exception(exc_type, exc_value, exc_tb, show_dialog)`

Enregistre une exception spécifique et optionnellement affiche une boîte de dialogue.

- Paramètres:
  - `exc_type`, `exc_value`, `exc_tb`: Détails de l'exception
  - `show_dialog`: Si `True`, affiche une notification à l'utilisateur

### Constant

```python
CRASHES_DIR = CONFIG_DIR / "crashes"
```

Chemin où sont stockés les rapports de plantage.

## Intégration dans le code existant

Pour reporter une exception capturée dans votre code:

### Approche 1: Utiliser la méthode `report_exception`

```python
try:
    # Votre code
    some_operation()
except Exception as e:
    import sys
    self.report_exception(type(e), e, sys.exc_info()[2], show_dialog=True)
```

### Approche 2: Laisser le gestionnaire global

Les exceptions non capturées seront automatiquement reportées par `sys.excepthook`.

### Approche 3: Utiliser le logging

Les exceptions enregistrées via `logger.exception()` seront capturées dans le fichier log:

```python
try:
    some_operation()
except Exception as e:
    logger.exception("Failed to perform operation")
```

## Limitations et notes

- Les rapports ne sont sauvegardés que lors de plantages non capturés
- Les exceptions capturées intentionnellement ne sont pas reportées automatiquement
- Le dossier `~/.config/clarionet/crashes/` peut croître indéfiniment; envisager une rotation des logs
- Les rapports contiennent la trace de pile complète; éviter de stocker des données sensibles en logs

## Améliorations futures

- [ ] Limite automatique de l'âge des rapports (p. ex., supprimer les rapports > 30 jours)
- [ ] Export des rapports (ZIP, CSV)
- [ ] Envoi optionnel des rapports à un serveur de monitoring
- [ ] Intégration avec un système de bug tracking (GitHub Issues, etc.)
- [ ] Analyse automatique des patterns d'erreurs fréquentes
- [ ] Dashboard visuel pour consulter les plantages

## Dépannage

### Aucun rapport de plantage n'est créé

1. Vérifiez que le dossier `~/.config/clarionet/crashes/` existe
2. Vérifiez les permissions d'écriture:
   ```bash
   ls -la ~/.config/clarionet/
   ```
3. Vérifiez les logs principaux:
   ```bash
   tail -f ~/.config/clarionet/clarionet.log
   ```

### Le rapport de plantage est vide ou corrompu

1. Vérifiez le format JSON:
   ```bash
   python3 -m json.tool ~/.config/clarionet/crashes/crash_*.json
   ```
2. Les rapports peuvent être corrompus si l'application se ferme abruptement (signal SIGKILL)

### La notification ne s'affiche pas

- Vérifiez que l'interface graphique Gtk est disponible
- Vérifiez que la fenêtre principale est bien initialisée avant l'appel à `check_for_pending_crash_reports`
