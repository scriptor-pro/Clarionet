# Building Clarionet for Windows

## Requirements

- Windows 10 or later
- Python 3.8+
- GTK3 (via msys2 or precompiled binaries)
- mpv
- PyInstaller
- Inno Setup (for installer generation)

## Build Steps

### 1. Install Dependencies

```powershell
# Install Python 3
# Download from https://www.python.org/downloads/

# Install PyInstaller
pip install pyinstaller

# Install GTK3 via MSYS2 or use precompiled binaries
# Download from https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

# Install mpv
# Download from https://mpv.io/installation/
```

### 2. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Generate Executable with PyInstaller

```powershell
pyinstaller Clarionet.spec --clean
```

This will create a standalone executable in `dist/Clarionet/` directory.

### 4. Prepare for Installer

```powershell
mkdir dist\packages\windows\clarionet
xcopy dist\Clarionet\* dist\packages\windows\clarionet\ /E /I
```

### 5. Generate Installer with Inno Setup

1. Download and install [Inno Setup](https://jrsoftware.org/isdl.php)
2. Update `packaging/windows/installer.iss`:
   - Replace `__VERSION__` with the actual version (e.g., 87.5.028)
   - Replace `__SOURCE_DIR__` with the project root directory
3. Open the script in Inno Setup and compile

Alternatively, use the command line:

```powershell
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /O"dist\packages\windows" `
  /D"MyAppVersion=87.5.028" `
  packaging\windows\installer.iss
```

### Output

The installer will be created at:
```
dist/packages/windows/clarionet-setup-87.5.028.exe
```

## Notes

- GTK3 is required to run Clarionet on Windows
- The bundled executable includes all dependencies except system libraries
- File size will be approximately 1.7GB (similar to Linux build)
- For distribution, ensure users have Python 3.8+ and GTK3 installed, or provide a full standalone bundle

## Troubleshooting

If you encounter GTK3 import errors:
1. Ensure GTK3 is properly installed
2. Set environment variables if needed
3. Use PyInstaller hooks for GTK binaries

See the `.spec` file for PyInstaller configuration details.
