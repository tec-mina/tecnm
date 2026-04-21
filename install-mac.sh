#!/usr/bin/env bash
# =============================================================================
# install-mac.sh — Instalación completa de PDF Extractor en macOS
#
# Uso:
#   chmod +x install-mac.sh
#   ./install-mac.sh            # instala dependencias locales Y construye Docker
#   ./install-mac.sh --docker   # solo construye la imagen Docker
#   ./install-mac.sh --local    # solo entorno Python local
# =============================================================================

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

ok()     { echo -e "${GREEN}  ✓ ${1}${RESET}"; }
info()   { echo -e "${CYAN}  → ${1}${RESET}"; }
warn()   { echo -e "${YELLOW}  ⚠ ${1}${RESET}"; }
die()    { echo -e "${RED}  ✗ ${1}${RESET}"; exit 1; }
header() { echo -e "\n${BOLD}${CYAN}── ${1} ──${RESET}"; }

# Rutas — el script vive en la raíz del repositorio
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$REPO_ROOT/pdf_extractor"

MODE="all"
for arg in "$@"; do
  case "$arg" in
    --docker) MODE="docker" ;;
    --local)  MODE="local"  ;;
    --help|-h)
      echo "Uso: $0 [--docker|--local]"
      echo "  (sin argumentos) instala entorno local Y construye Docker"
      exit 0 ;;
  esac
done

echo -e "\n${BOLD}PDF Extractor — Instalador macOS${RESET}"
echo "======================================"

# ── Homebrew ──────────────────────────────────────────────────────────────────
header "Homebrew"
if ! command -v brew &>/dev/null; then
  info "Instalando Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [[ -f /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
  fi
fi
ok "Homebrew $(brew --version | head -1)"

# ── Docker ────────────────────────────────────────────────────────────────────
if [[ "$MODE" == "docker" || "$MODE" == "all" ]]; then
  header "Docker Desktop"
  if ! command -v docker &>/dev/null; then
    info "Instalando Docker Desktop..."
    brew install --cask docker
    open -a Docker 2>/dev/null || true
    echo ""
    warn "Docker Desktop se está abriendo. Espera a que el ícono en la barra de menú deje de moverse."
    read -rp "  Presiona ENTER cuando Docker esté listo: " _
  fi
  ok "Docker $(docker --version)"

  info "Construyendo imagen pdf-extractor:latest ..."
  docker build \
    -f "$PROJECT_DIR/docker/Dockerfile" \
    -t pdf-extractor:latest \
    "$REPO_ROOT"
  ok "Imagen pdf-extractor:latest lista"

  echo ""
  echo -e "${BOLD}Uso con Docker:${RESET}"
  echo "  docker run --rm \\"
  echo "    -v \$(pwd):/app/input \\"
  echo "    -v \$(pwd)/output:/app/output \\"
  echo "    pdf-extractor:latest extract /app/input/documento.pdf -o /app/output"
fi

# ── Entorno local Python ──────────────────────────────────────────────────────
if [[ "$MODE" == "local" || "$MODE" == "all" ]]; then
  header "Dependencias del sistema"
  BREW_PACKAGES=(
    tesseract tesseract-lang
    poppler ghostscript qpdf
    unpaper imagemagick
    openjdk@17
    exiftool mupdf-tools
  )
  for pkg in "${BREW_PACKAGES[@]}"; do
    if brew list --formula "$pkg" &>/dev/null 2>&1; then
      ok "$pkg (ya instalado)"
    else
      info "Instalando $pkg..."
      brew install "$pkg"
      ok "$pkg"
    fi
  done

  # Java en PATH
  if ! command -v java &>/dev/null; then
    JAVA_BIN="$(brew --prefix openjdk@17)/bin"
    export PATH="$JAVA_BIN:$PATH"
    echo "export PATH=\"$JAVA_BIN:\$PATH\"" >> ~/.zprofile
  fi
  ok "Java $(java -version 2>&1 | head -1)"

  header "Python y entorno virtual"
  PYTHON=$(command -v python3.11 2>/dev/null || command -v python3 || die "Python 3.10+ no encontrado")
  ok "Python $($PYTHON --version)"

  VENV="$PROJECT_DIR/.venv"
  if [[ ! -d "$VENV" ]]; then
    info "Creando entorno virtual..."
    "$PYTHON" -m venv "$VENV"
  fi
  ok "Entorno virtual: $VENV"

  "$VENV/bin/pip" install --upgrade pip --quiet
  info "Instalando dependencias Python (base + ocr + advanced)..."
  "$VENV/bin/pip" install \
    -r "$PROJECT_DIR/requirements/base.txt" \
    -r "$PROJECT_DIR/requirements/ocr.txt" \
    -r "$PROJECT_DIR/requirements/advanced.txt" \
    --quiet
  ok "Dependencias Python instaladas"

  # Activación automática en nuevas sesiones
  ACTIVATE="source $VENV/bin/activate"
  if ! grep -qF "$ACTIVATE" ~/.zshrc 2>/dev/null; then
    { echo ""; echo "# pdf-extractor"; echo "$ACTIVATE"; } >> ~/.zshrc
    info "Activación del venv agregada a ~/.zshrc"
  fi

  header "Verificación"
  source "$VENV/bin/activate"
  python -m pdf_extractor capabilities || true

  echo ""
  echo -e "${BOLD}Uso local:${RESET}"
  echo "  source $VENV/bin/activate"
  echo "  python -m pdf_extractor extract documento.pdf -o salida/"
  echo "  python -m pdf_extractor web   # interfaz web en http://localhost:5000"
fi

echo ""
echo -e "${BOLD}${GREEN}Instalación completada.${RESET}"
