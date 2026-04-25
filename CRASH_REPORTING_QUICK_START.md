# 🚀 Guide Rapide: Système de Rapport de Plantage

## Installation

```bash
# Configuration automatique (optionnel)
bash setup_crash_reporting.sh
```

## Utilisation

### Consulter les plantages

```bash
# Lister tous les rapports
python3 crash_reporter.py list

# Afficher les détails d'un rapport
python3 crash_reporter.py show <ID>

# Exemples:
python3 crash_reporter.py show 2026-04-25_14-30-15
```

### Supprimer les plantages

```bash
# Supprimer un rapport spécifique
python3 crash_reporter.py delete 2026-04-25_14-30-15

# Supprimer tous les rapports
python3 crash_reporter.py delete --all
```

### Tester le système

```bash
# Créer un rapport de test
python3 test_crash_reporting.py
```

## Où sont stockés les rapports ?

```
~/.config/clarionet/crashes/crash_*.json
```

## Fonctionnement automatique

✅ **À chaque démarrage:**
- Clarionet détecte automatiquement les plantages précédents
- Une notification modale affiche les détails du plantage
- L'ID unique du rapport est visible pour transmission au développeur

✅ **Lors d'un plantage:**
- Un rapport JSON est créé automatiquement
- La trace de pile complète est enregistrée
- Les métadonnées (version, plateforme) sont incluses

## Format des rapports

Chaque rapport est un fichier JSON contenant:

```json
{
  "crash_id": "crash_2026-04-25_10-02-51_3902383f",
  "timestamp": "2026-04-25_10-02-51",
  "app_name": "Clarionet",
  "app_version": "87.5.028",
  "exception_type": "ZeroDivisionError",
  "exception_message": "division by zero",
  "traceback": "...",
  "python_version": "3.11.2",
  "platform": "linux"
}
```

## Intégration dans le code

Pour rapporter manuellement une exception:

```python
try:
    some_operation()
except Exception:
    import sys
    self.report_exception(*sys.exc_info(), show_dialog=True)
```

## Documentation complète

Voir `CRASH_REPORTING.md` pour:
- Architecture technique détaillée
- Guide d'intégration pour développeurs
- Limitations et considérations
- Suggestions d'améliorations

## Questions fréquentes

**Q: Où sont stockés les rapports?**
A: `~/.config/clarionet/crashes/`

**Q: Les rapports prennent-ils beaucoup d'espace?**
A: Non, en général < 10 KB par rapport. Envisager une rotation après 30 jours en production.

**Q: Comment puis-je partager un rapport avec le développeur?**
A: Envoyez l'ID unique affiché à la notification, ou l'ID du fichier JSON trouvé dans le dossier crashes.

**Q: Que contient un rapport?**
A: Type d'erreur, message, trace de pile complète, version app, version Python, plateforme.

**Q: Les données sensibles sont-elles exposées?**
A: Les rapports contiennent ce qui est en logs; éviter de logger des données sensibles.

## Commandes utiles

```bash
# Voir tous les rapports (format tableau)
python3 crash_reporter.py list

# Voir un rapport spécifique
python3 crash_reporter.py show 2026-04-25

# Voir le dernier rapport
python3 crash_reporter.py show $(python3 crash_reporter.py list | tail -1 | awk '{print $1}')

# Supprimer les vieux rapports (> 30 jours)
find ~/.config/clarionet/crashes -name "*.json" -mtime +30 -delete

# Exporter tous les rapports
tar czf clarionet_crashes.tar.gz ~/.config/clarionet/crashes/
```

## Alias shell (optionnel)

Si vous avez exécuté `setup_crash_reporting.sh` avec l'option alias:

```bash
clarionet-crashes        # Lister tous les rapports
clarionet-crash-show <ID> # Voir les détails
clarionet-crash-clean    # Supprimer tous les rapports
clarionet-crash-test     # Tester le système
```

---

**🎯 Point clé:** Le système fonctionne automatiquement. Vous n'avez rien à faire sauf consulter les rapports en cas de besoin !
