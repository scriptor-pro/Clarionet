#!/usr/bin/env python3
"""
Script de test pour démontrer le système de rapport de plantage.
Ce script simule un plantage et génère un rapport pour la démonstration.
"""

import json
import sys
import traceback
from pathlib import Path
from datetime import datetime
import uuid


def create_test_crash_report():
    """Crée un rapport de plantage de test."""
    config_dir = Path.home() / ".config" / "clarionet"
    crashes_dir = config_dir / "crashes"
    crashes_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    crash_id = f"crash_TEST_{timestamp}_{uuid.uuid4().hex[:8]}"
    crash_file = crashes_dir / f"{crash_id}.json"

    try:
        x = 1
        y = 0
        result = x / y
    except Exception as e:
        exc_type = type(e)
        exc_value = e
        tb = sys.exc_info()[2]
        tb_lines = traceback.format_exception(exc_type, exc_value, tb)

        crash_data = {
            "crash_id": crash_id,
            "timestamp": timestamp,
            "app_name": "Clarionet",
            "app_version": "87.5.028",
            "exception_type": exc_type.__name__,
            "exception_message": str(exc_value),
            "traceback": "".join(tb_lines),
            "python_version": sys.version,
            "platform": sys.platform,
        }

        with open(crash_file, "w", encoding="utf-8") as f:
            json.dump(crash_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Rapport de plantage de test créé: {crash_file}")
        print(f"📊 ID du rapport: {crash_id}")
        print(f"\n💡 Pour afficher ce rapport, exécutez:")
        print(f"   python3 crash_reporter.py show {timestamp}")
        print(f"\n💡 Pour voir tous les rapports:")
        print(f"   python3 crash_reporter.py list")

        return crash_file


if __name__ == "__main__":
    create_test_crash_report()
