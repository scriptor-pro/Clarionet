# Clarionet

Application minimaliste pour écouter des radios en ligne. Disponible sur Linux, Windows et macOS.

## Version

87.5.027

## Installation

### Linux

#### Prérequis
- Python 3.8+
- GTK3 + PyGObject
- mpv

#### Depuis les sources
```bash
git clone https://github.com/yourusername/clarionet.git
cd clarionet
pip install -r requirements.txt
./install.sh
./clarionet
```

#### Depuis un paquet
- **Debian/Ubuntu**: `sudo apt install ./clarionet_0.2.1_amd64.deb`
- **Fedora/RHEL**: `sudo rpm -i clarionet-0.2.1-1.x86_64.rpm`

### Windows

#### Prérequis
- Windows 10 ou ultérieur
- Python 3.8+ ([Télécharger](https://www.python.org/downloads/))
- mpv ([Télécharger](https://mpv.io/installation/))

#### Installation
1. Cloner ou télécharger le projet
2. Ouvrir un terminal (PowerShell ou Cmd) dans le dossier du projet
3. Installer les dépendances Python :
   ```powershell
   pip install -r requirements.txt
   ```
4. Lancer l'application :
   ```powershell
   python clarionet.py
   ```

#### Build Windows (optionnel, avec PyInstaller)
```powershell
pip install pyinstaller
pyinstaller Clarionet.spec
```
L'exécutable se trouvera dans `dist/Clarionet/`

### macOS

#### Prérequis
- macOS 10.13 ou ultérieur
- Python 3.8+ (via [Homebrew](https://brew.sh/) ou python.org)
- mpv

#### Installation via Homebrew (recommandé)
```bash
# Installer les dépendances
brew install python3 gtk3 mpv

# Cloner le projet
git clone https://github.com/yourusername/clarionet.git
cd clarionet

# Installer les dépendances Python
pip3 install -r requirements.txt

# Lancer l'application
python3 clarionet.py
```

#### Installation manuelle
1. Télécharger et installer Python 3 depuis [python.org](https://www.python.org/downloads/)
2. Installer GTK3 et mpv
3. Cloner le projet et installer les dépendances comme ci-dessus

#### Build macOS (optionnel, avec PyInstaller)
```bash
pip install pyinstaller
pyinstaller Clarionet.spec
```
L'application sera disponible dans `dist/Clarionet.app/`

## Utilisation

### Lancer l'application

**Linux/macOS:**
```bash
./clarionet
```

**Windows:**
```powershell
python clarionet.py
```

### Raccourcis clavier

- **Lecture/Pause**: `Espace`
- **Arrêt**: `S`
- **Volume**: `Flèche gauche` / `Flèche droite`
- **Radio précédente/suivante**: `Flèche haut` / `Flèche bas`
- **Ajouter une radio**: `Ctrl+N`
- **Gérer les radios**: `Ctrl+M`
- **Quitter**: `Ctrl+Q`

## Données

Les fichiers de configuration sont stockés dans :
- **Linux/macOS**: `~/.config/clarionet/`
- **Windows**: `%APPDATA%\clarionet\`

Fichiers:
- `radios.json` - Liste des radios (id, name, stream_url)
- `config.json` - Paramètres de l'application (volume, dernière radio)
- `clarionet.log` - Fichier journal
- `clarionet-mpv.log` - Journal mpv

## Dépendances Python

Voir `requirements.txt` pour la liste complète des dépendances Python.

## Développement

### Dépendances de développement
```bash
pip install -r requirements-dev.txt
```

### Build distribué
- **Linux**: Support .deb et .rpm
- **Windows**: Exécutable via PyInstaller
- **macOS**: Bundle .app via PyInstaller

## Licence

MIT
