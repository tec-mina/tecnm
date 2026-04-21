# =============================================================================
# install-windows.ps1 — Instalación completa de PDF Extractor en Windows
#
# Uso (PowerShell como Administrador):
#   Set-ExecutionPolicy Bypass -Scope Process -Force
#   .\install-windows.ps1               # instala dependencias locales Y Docker
#   .\install-windows.ps1 -Mode docker  # solo construye imagen Docker
#   .\install-windows.ps1 -Mode local   # solo entorno Python local
# =============================================================================

param(
    [ValidateSet("all","docker","local")]
    [string]$Mode = "all"
)

$ErrorActionPreference = "Stop"

function Ok($msg)     { Write-Host "  [OK] $msg" -ForegroundColor Green  }
function Info($msg)   { Write-Host "  --> $msg"  -ForegroundColor Cyan   }
function Warn($msg)   { Write-Host "  [!] $msg"  -ForegroundColor Yellow }
function Header($msg) { Write-Host "`n-- $msg --" -ForegroundColor Cyan  }
function Die($msg)    { Write-Host "  [ERR] $msg" -ForegroundColor Red; exit 1 }

function Test-Cmd($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

function Winget-Install($id, $label) {
    if (Test-Cmd winget) {
        Info "Instalando $label..."
        winget install -e --id $id `
            --accept-package-agreements --accept-source-agreements --silent
        Ok "$label instalado"
    } else {
        Die "winget no disponible. Instala $label manualmente."
    }
}

# Rutas — el script vive en la raíz del repositorio
$RepoRoot   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Join-Path $RepoRoot "pdf_extractor"

Write-Host "`nPDF Extractor — Instalador Windows" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "======================================" -ForegroundColor Cyan

# ── winget ────────────────────────────────────────────────────────────────────
Header "Gestor de paquetes"
if (Test-Cmd winget)  { Ok "winget disponible" }
elseif (Test-Cmd choco) { Ok "Chocolatey (fallback)" }
else { Warn "winget no encontrado. Actualiza 'App Installer' desde Microsoft Store." }

# ── Docker ────────────────────────────────────────────────────────────────────
if ($Mode -eq "docker" -or $Mode -eq "all") {
    Header "Docker Desktop"
    if (-not (Test-Cmd docker)) {
        Winget-Install "Docker.DockerDesktop" "Docker Desktop"
        Warn "Abre Docker Desktop, completa la configuracion inicial y reinicia PowerShell."
        Warn "Luego vuelve a ejecutar: .\install-windows.ps1 -Mode docker"
        Read-Host "Presiona ENTER para continuar de todas formas"
        # Refrescar PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" +
                    [System.Environment]::GetEnvironmentVariable("PATH","User")
    }
    if (Test-Cmd docker) {
        Ok "$(docker --version)"
        Info "Construyendo imagen pdf-extractor:latest..."
        docker build `
            -f "$ProjectDir\docker\Dockerfile" `
            -t pdf-extractor:latest `
            $RepoRoot
        Ok "Imagen pdf-extractor:latest lista"
        Write-Host ""
        Write-Host "Uso con Docker:" -ForegroundColor White
        Write-Host '  docker run --rm -v "${PWD}:/app/input" -v "${PWD}/output:/app/output" \'
        Write-Host '    pdf-extractor:latest extract /app/input/documento.pdf -o /app/output'
    }
}

# ── Entorno local ─────────────────────────────────────────────────────────────
if ($Mode -eq "local" -or $Mode -eq "all") {

    Header "Python 3.11"
    if (-not (Test-Cmd python)) { Winget-Install "Python.Python.3.11" "Python 3.11" }
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("PATH","User")
    Ok "$(python --version)"

    Header "Java 17 (Tabula + Apache Tika)"
    if (-not (Test-Cmd java)) {
        Winget-Install "EclipseAdoptium.Temurin.17.JDK" "Java 17"
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" +
                    [System.Environment]::GetEnvironmentVariable("PATH","User")
    }
    Ok "Java instalado"

    Header "Tesseract OCR"
    if (-not (Test-Cmd tesseract)) {
        Winget-Install "UB-Mannheim.TesseractOCR" "Tesseract OCR"
        $tdir = "C:\Program Files\Tesseract-OCR"
        $cur  = [System.Environment]::GetEnvironmentVariable("PATH","Machine")
        if ($cur -notlike "*$tdir*") {
            [System.Environment]::SetEnvironmentVariable("PATH","$cur;$tdir","Machine")
        }
        [System.Environment]::SetEnvironmentVariable("TESSDATA_PREFIX","$tdir\tessdata","Machine")
        $env:PATH += ";$tdir"
        $env:TESSDATA_PREFIX = "$tdir\tessdata"
    }
    Ok "Tesseract instalado"

    Header "Ghostscript"
    if (-not (Test-Cmd gs)) { Winget-Install "GPL.Ghostscript" "Ghostscript" }
    else { Ok "Ghostscript ya instalado" }

    Header "Poppler (pdfinfo, pdfimages)"
    if (-not (Test-Cmd pdfinfo)) {
        Info "Descargando Poppler para Windows..."
        $url  = "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.02.0-0/Release-24.02.0-0.zip"
        $zip  = "$env:TEMP\poppler.zip"
        $dest = "C:\Tools\poppler"
        Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
        Expand-Archive -Path $zip -DestinationPath $dest -Force
        Remove-Item $zip -Force
        $bin = (Get-ChildItem $dest -Recurse -Filter "pdfinfo.exe" |
                Select-Object -First 1).Directory.FullName
        if ($bin) {
            $cur = [System.Environment]::GetEnvironmentVariable("PATH","Machine")
            if ($cur -notlike "*$bin*") {
                [System.Environment]::SetEnvironmentVariable("PATH","$cur;$bin","Machine")
                $env:PATH += ";$bin"
            }
            Ok "Poppler en $bin"
        } else {
            Warn "Poppler descargado en $dest. Agrega su carpeta 'bin' al PATH manualmente."
        }
    } else { Ok "Poppler ya instalado" }

    Header "ImageMagick"
    if (-not (Test-Cmd magick)) { Winget-Install "ImageMagick.ImageMagick" "ImageMagick" }
    else { Ok "ImageMagick ya instalado" }

    Header "ExifTool"
    if (-not (Test-Cmd exiftool)) { Winget-Install "OliverBetz.ExifTool" "ExifTool" }
    else { Ok "ExifTool ya instalado" }

    Header "Entorno virtual y dependencias Python"
    $venv = "$ProjectDir\.venv"
    if (-not (Test-Path $venv)) {
        Info "Creando entorno virtual..."
        python -m venv $venv
    }
    Ok "Entorno virtual: $venv"

    $pip = "$venv\Scripts\pip.exe"
    & $pip install --upgrade pip --quiet
    Info "Instalando dependencias Python..."
    & $pip install `
        -r "$ProjectDir\requirements\base.txt" `
        -r "$ProjectDir\requirements\ocr.txt" `
        -r "$ProjectDir\requirements\advanced.txt" `
        --quiet
    Ok "Dependencias instaladas"

    Header "Verificacion"
    & "$venv\Scripts\python.exe" -m pdf_extractor capabilities

    Write-Host ""
    Write-Host "Uso local:" -ForegroundColor White
    Write-Host "  $venv\Scripts\Activate.ps1"
    Write-Host "  python -m pdf_extractor extract documento.pdf -o salida\"
    Write-Host "  python -m pdf_extractor web   # interfaz web en http://localhost:5000"
}

Write-Host ""
Write-Host "Instalacion completada." -ForegroundColor Green
