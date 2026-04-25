# Résumé: Mécanisme de Rapport de Plantage pour Clarionet

## 📋 Ce qui a été ajouté

Un système complet de capture, d'enregistrement et de consultation des rapports de plantage a été intégré à Clarionet.

### 1. **Modifications du fichier `clarionet.py`**

#### Nouvelles importations
- `traceback`: Pour capturer les traces de pile des exceptions
- `datetime`: Pour timestamper les rapports

#### Nouvelles constantes
- `CRASHES_DIR`: Répertoire de stockage des rapports (`~/.config/clarionet/crashes/`)

#### Nouvelles fonctions globales

**`create_crash_report(exc_type, exc_value, tb)`**
- Crée un fichier JSON structuré avec tous les détails du plantage
- Retourne: `(crash_id, crash_file)`
- Contient:
  - Type et message d'exception
  - Trace de pile complète
  - Métadonnées (version app, Python, plateforme)

**`setup_crash_handler()`**
- Configure le gestionnaire global d'exceptions (`sys.excepthook`)
- Intercepte tous les plantages non gérés
- Appelle `create_crash_report()` automatiquement
- Doit être appelée au démarrage

**`check_for_pending_crash_reports(window)`**
- Vérifie les plantages précédents au démarrage
- Affiche une notification modale pour chaque plantage détecté
- Affiche jusqu'aux 5 plantages les plus récents

#### Nouvelles méthodes de classe

**`ClarionetApp.report_exception(exc_type, exc_value, exc_tb, show_dialog=False)`**
- Permet de reporter manuellement une exception capturée
- Optionnellement affiche une boîte de dialogue à l'utilisateur
- Enregistre l'exception dans un rapport JSON

#### Modifications existantes

- Initialisation du gestionnaire au démarrage (`if __name__ == "__main__"`)
- Appel de `check_for_pending_crash_reports()` lors de l'activation de l'app

### 2. **Nouveaux fichiers**

#### `crash_reporter.py` (Script utilitaire)

Outil CLI pour consulter et gérer les rapports de plantage:

```bash
# Lister tous les rapports
python3 crash_reporter.py list

# Afficher les détails d'un rapport
python3 crash_reporter.py show <ID>

# Supprimer des rapports
python3 crash_reporter.py delete <ID>
python3 crash_reporter.py delete --all
```

Fonctionnalités:
- Interface utilisateur en couleurs avec emojis
- Recherche flexible par ID ou pattern
- Affichage formaté des traces de pile
- Gestion d'erreurs robuste

#### `test_crash_reporting.py` (Script de démonstration)

Script pour tester le système en créant un plantage simulé:

```bash
python3 test_crash_reporting.py
```

Génère un rapport de plantage de test pour vérifier que le système fonctionne correctement.

#### `CRASH_REPORTING.md` (Documentation complète)

Documentation technique détaillée:
- Vue d'ensemble du système
- Guide d'utilisation (interface GUI et CLI)
- Architecture technique
- Intégration dans le code
- Limitations et notes
- Suggestions d'améliorations
- Guide de dépannage

## 🎯 Résumé des fonctionnalités

| Fonctionnalité | Description |
|---|---|
| **Capture automatique** | Tous les plantages non gérés sont capturés automatiquement |
| **Stockage structuré** | Format JSON avec toutes les métadonnées pertinentes |
| **Notification au démarrage** | Alerte utilisateur si des plantages sont détectés |
| **Consultation CLI** | Script Python pour examiner les rapports |
| **Suppression facile** | Nettoyage des rapports anciens ou obsolètes |
| **Trace de pile complète** | Contexte complet pour le débogage |
| **Métadonnées environnement** | Version Python, plateforme, version app |

## 📁 Stockage

Les rapports sont sauvegardés dans:
```
~/.config/clarionet/crashes/crash_YYYY-MM-DD_HH-MM-SS_XXXXXXXX.json
```

Chaque rapport est un fichier JSON valide, facilement exploitable par d'autres outils.

## 🚀 Utilisation

### Pour l'utilisateur final

1. Clarionet détecte automatiquement les plantages
2. Au prochain lancement, une notification affiche le détail du plantage
3. L'utilisateur peut noter l'ID du rapport pour le développeur

### Pour le développeur

1. **Consulter les rapports:**
   ```bash
   python3 crash_reporter.py list      # Voir tous les rapports
   python3 crash_reporter.py show 2026-04-25  # Voir les détails
   ```

2. **Intégrer dans le code existant:**
   ```python
   try:
       something()
   except Exception:
       self.report_exception(*sys.exc_info(), show_dialog=True)
   ```

## ✅ Validation

Le système a été testé et validé:
- ✅ Compilation Python réussie
- ✅ Syntaxe correcte des scripts
- ✅ Création de rapports de test
- ✅ Consultation des rapports
- ✅ Suppression des rapports
- ✅ Affichage formaté avec métadonnées

## 📝 Prochaines étapes recommandées

1. **En production**: Tester avec de vrais scénarios de plantage
2. **Monitoring**: Implémenter la rotation des logs (supprimer rapports > 30 jours)
3. **Partage**: Permettre l'export des rapports pour l'analyse
4. **Centralisation**: Envisager l'envoi optionnel à un serveur de telemetry
5. **UI**: Ajouter un menu dans Clarionet pour accéder aux rapports
