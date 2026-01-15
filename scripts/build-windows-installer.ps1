$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$version = $env:VERSION
if (-not $version) {
  $versionLine = Select-String -Path "$root\radiocity.py" -Pattern '^APP_VERSION' | Select-Object -First 1
  if ($versionLine) {
    $version = $versionLine.Line.Split('"')[1]
  } else {
    $version = "0.0.0"
  }
}

$distDir = Join-Path $root "dist"
$buildDir = Join-Path $distDir "clarionet"
$venvDir = Join-Path $root ".venv-win"
$iconPath = Join-Path $root "assets\icons\clarionet.ico"

if (Test-Path $buildDir) { Remove-Item $buildDir -Recurse -Force }
New-Item -ItemType Directory -Force -Path $buildDir | Out-Null

if (-not (Test-Path $venvDir)) {
  python -m venv $venvDir
}

& "$venvDir\Scripts\pip" install --upgrade pip | Out-Null
if (Test-Path "$root\requirements.txt") {
  & "$venvDir\Scripts\pip" install -r "$root\requirements.txt" pyinstaller | Out-Null
} else {
  & "$venvDir\Scripts\pip" install pyinstaller | Out-Null
}

$iconArgs = @()
if (Test-Path $iconPath) {
  $iconArgs = @("--icon", $iconPath)
}

& "$venvDir\Scripts\pyinstaller" `
  --noconfirm `
  --name "clarionet" `
  --windowed `
  --add-data "$root\assets;assets" `
  @iconArgs `
  "$root\radiocity.py"

$exeSource = Join-Path $root "dist\clarionet\clarionet.exe"
if (-not (Test-Path $exeSource)) {
  throw "Executable not found at $exeSource"
}

$issTemplate = Get-Content "$root\packaging\windows\installer.iss" -Raw
$issContent = $issTemplate.Replace("__VERSION__", $version).Replace("__SOURCE_DIR__", $root)
$issPath = Join-Path $root "dist\clarionet-installer.iss"
Set-Content -Path $issPath -Value $issContent -Encoding ASCII

$inno = Get-Command "iscc" -ErrorAction SilentlyContinue
if (-not $inno) {
  throw "Inno Setup (iscc.exe) not found. Install Inno Setup and ensure iscc is in PATH."
}

& $inno.Path $issPath

Write-Host "Built installer in $distDir"
