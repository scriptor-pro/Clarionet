#!/usr/bin/env python3
"""Utilitaire pour consulter et gérer les rapports de plantage de Clarionet."""

import json
import sys
from pathlib import Path
from datetime import datetime


def get_crashes_dir():
    """Retourne le chemin du dossier des rapports de plantage."""
    return Path.home() / ".config" / "clarionet" / "crashes"


def list_crashes():
    """Affiche la liste de tous les rapports de plantage."""
    crashes_dir = get_crashes_dir()

    if not crashes_dir.exists():
        print("Aucun rapport de plantage trouvé.")
        return

    crash_files = sorted(crashes_dir.glob("*.json"))

    if not crash_files:
        print("Aucun rapport de plantage trouvé.")
        return

    print(f"📋 {len(crash_files)} rapport(s) de plantage trouvé(s):\n")
    print(f"{'ID':<50} {'Type':<20} {'Date/Heure':<20}")
    print("-" * 90)

    for crash_file in crash_files:
        try:
            with open(crash_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                crash_id = data.get("crash_id", "?")[:47]
                exc_type = data.get("exception_type", "?")[:17]
                timestamp = data.get("timestamp", "?")
                print(f"{crash_id:<50} {exc_type:<20} {timestamp:<20}")
        except json.JSONDecodeError:
            print(f"❌ Fichier invalide: {crash_file.name}")


def show_crash_details(crash_id):
    """Affiche les détails d'un rapport de plantage spécifique."""
    crashes_dir = get_crashes_dir()

    crash_files = sorted(crashes_dir.glob(f"*{crash_id}*.json"))

    if not crash_files:
        print(f"❌ Aucun rapport trouvé pour l'ID: {crash_id}")
        return

    crash_file = crash_files[-1]

    try:
        with open(crash_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        print("\n" + "=" * 80)
        print("📄 RAPPORT DE PLANTAGE")
        print("=" * 80)

        print(f"\n🔍 Identifiant: {data.get('crash_id', 'N/A')}")
        print(f"📅 Date/Heure: {data.get('timestamp', 'N/A')}")
        print(f"📱 Application: {data.get('app_name', 'N/A')} v{data.get('app_version', 'N/A')}")

        print(f"\n⚠️  EXCEPTION")
        print("-" * 80)
        print(f"Type: {data.get('exception_type', 'N/A')}")
        print(f"Message: {data.get('exception_message', 'N/A')}")

        print(f"\n🐍 TRACEBACK")
        print("-" * 80)
        print(data.get("traceback", "N/A"))

        print(f"\n💻 ENVIRONNEMENT")
        print("-" * 80)
        print(f"Python: {data.get('python_version', 'N/A')}")
        print(f"Plateforme: {data.get('platform', 'N/A')}")

        print("\n" + "=" * 80 + "\n")

    except json.JSONDecodeError:
        print(f"❌ Impossible de lire le fichier: {crash_file}")
    except Exception as e:
        print(f"❌ Erreur: {e}")


def delete_crashes(pattern="*"):
    """Supprime les rapports de plantage."""
    crashes_dir = get_crashes_dir()

    if not crashes_dir.exists():
        print("Aucun rapport de plantage trouvé.")
        return

    if pattern == "*":
        crash_files = sorted(crashes_dir.glob("*.json"))
    else:
        crash_files = sorted(crashes_dir.glob(f"*{pattern}*.json"))

    if not crash_files:
        print("Aucun rapport correspondant trouvé.")
        return

    for crash_file in crash_files:
        try:
            crash_file.unlink()
            print(f"✅ Supprimé: {crash_file.name}")
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de {crash_file.name}: {e}")

    print(f"\n✨ {len(crash_files)} rapport(s) supprimé(s).")


def main():
    """Point d'entrée principal."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  crash_reporter.py list          - Lister tous les rapports")
        print("  crash_reporter.py show <ID>     - Afficher les détails d'un rapport")
        print("  crash_reporter.py delete [ID]   - Supprimer les rapports")
        print("  crash_reporter.py delete --all  - Supprimer tous les rapports")
        return

    command = sys.argv[1]

    if command == "list":
        list_crashes()
    elif command == "show":
        if len(sys.argv) < 3:
            print("❌ Veuillez spécifier un ID de rapport")
            return
        show_crash_details(sys.argv[2])
    elif command == "delete":
        if len(sys.argv) < 3:
            print("❌ Veuillez spécifier un ID ou utiliser --all")
            return
        pattern = "*" if sys.argv[2] == "--all" else sys.argv[2]
        delete_crashes(pattern)
    else:
        print(f"❌ Commande inconnue: {command}")


if __name__ == "__main__":
    main()
