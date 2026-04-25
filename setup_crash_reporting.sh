#!/bin/bash

# Script de setup pour configurer le système de rapport de plantage
# Usage: bash setup_crash_reporting.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$HOME/.config/clarionet"
CRASHES_DIR="$CONFIG_DIR/crashes"

echo "🚀 Configuration du système de rapport de plantage pour Clarionet"
echo ""

# Créer les répertoires
echo "📁 Création des répertoires..."
mkdir -p "$CRASHES_DIR"
echo "   ✅ $CRASHES_DIR"

# Rendre les scripts exécutables
echo ""
echo "🔧 Rendre les scripts exécutables..."
chmod +x "$SCRIPT_DIR/crash_reporter.py"
echo "   ✅ crash_reporter.py"

chmod +x "$SCRIPT_DIR/test_crash_reporting.py"
echo "   ✅ test_crash_reporting.py"

# Création d'alias (optionnel)
if [ -f "$HOME/.bashrc" ] || [ -f "$HOME/.zshrc" ]; then
    echo ""
    read -p "Ajouter des alias shell pour crash_reporter.py ? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ALIAS_TEXT="
# Clarionet crash reporting aliases
alias clarionet-crashes='python3 $SCRIPT_DIR/crash_reporter.py list'
alias clarionet-crash-show='python3 $SCRIPT_DIR/crash_reporter.py show'
alias clarionet-crash-clean='python3 $SCRIPT_DIR/crash_reporter.py delete --all'
alias clarionet-crash-test='python3 $SCRIPT_DIR/test_crash_reporting.py'
"

        if [ -f "$HOME/.bashrc" ]; then
            echo "$ALIAS_TEXT" >> "$HOME/.bashrc"
            echo "   ✅ Alias ajoutés à ~/.bashrc"
        fi

        if [ -f "$HOME/.zshrc" ]; then
            echo "$ALIAS_TEXT" >> "$HOME/.zshrc"
            echo "   ✅ Alias ajoutés à ~/.zshrc"
        fi

        echo ""
        echo "💡 Rechargez votre shell ou exécutez 'source ~/.bashrc' (ou ~/.zshrc)"
    fi
fi

# Test optionnel
echo ""
read -p "Tester le système avec un plantage simulé ? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🧪 Création d'un rapport de test..."
    python3 "$SCRIPT_DIR/test_crash_reporting.py"

    echo ""
    echo "📋 Affichage des rapports..."
    python3 "$SCRIPT_DIR/crash_reporter.py" list
fi

echo ""
echo "✨ Configuration terminée !"
echo ""
echo "📖 Documentation: Voir CRASH_REPORTING.md pour plus de détails"
echo ""
echo "Commandes disponibles:"
echo "  • python3 crash_reporter.py list       - Lister les plantages"
echo "  • python3 crash_reporter.py show <ID>  - Voir les détails"
echo "  • python3 crash_reporter.py delete <ID> - Supprimer un rapport"
echo "  • python3 crash_reporter.py delete --all - Supprimer tous"
echo ""
