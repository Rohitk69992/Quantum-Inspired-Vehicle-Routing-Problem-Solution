#!/usr/bin/env bash
# ==============================================================================
# build.sh - Single-Entrypoint Reproducibility Pipeline
# "A SUMO-Based Framework for Traffic-Aware Vehicle Routing"
# Author: Rohit Korade (ISBM College of Engineering, Pune, India)
# ==============================================================================

set -eo pipefail

LOG_FILE="build.log"
exec > >(tee -a "${LOG_FILE}") 2>&1

echo "================================================================================"
echo "IEEE T-ITS REPRODUCIBILITY BUILD: $(date)"
echo "================================================================================"

# Default arguments
MODE="--quick"
STAGES_ARG=""

# Parse flags
while [[ $# -gt 0 ]]; do
  case $1 in
    --quick)
      MODE="--quick"
      shift
      ;;
    --full)
      MODE="--full"
      shift
      ;;
    --stages)
      shift
      STAGES_ARG="--stages $@"
      break
      ;;
    --help|-h)
      echo "Usage: bash build.sh [--quick | --full] [--stages stage1 stage2 ...]"
      echo "  --quick  : Fast audit and paper verification using raw benchmark data (default)"
      echo "  --full   : Full execution including solver and simulation checks"
      echo "  --stages : Run specific stages: audit alns budget mip reroute congestion qaoa pyvrp tables figures claims verify"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

# Detect Python executable
if command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
elif command -v python.exe >/dev/null 2>&1; then
  PYTHON_CMD="python.exe"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
else
  PYTHON_CMD="py"
fi

# Detect LaTeX executables
if command -v latexmk.exe >/dev/null 2>&1; then
  LATEXMK_CMD="latexmk.exe"
elif command -v latexmk >/dev/null 2>&1; then
  LATEXMK_CMD="latexmk"
else
  LATEXMK_CMD=""
fi

if command -v pdflatex.exe >/dev/null 2>&1; then
  PDFLATEX_CMD="pdflatex.exe"
elif command -v pdflatex >/dev/null 2>&1; then
  PDFLATEX_CMD="pdflatex"
else
  PDFLATEX_CMD=""
fi

if command -v bibtex.exe >/dev/null 2>&1; then
  BIBTEX_CMD="bibtex.exe"
elif command -v bibtex >/dev/null 2>&1; then
  BIBTEX_CMD="bibtex"
else
  BIBTEX_CMD=""
fi

echo "Configuration: Mode=${MODE} ${STAGES_ARG}"
echo "Using Python: ${PYTHON_CMD}"

# Trap for failure
trap 'echo "[ERROR] build.sh failed at line $LINENO. See ${LOG_FILE} for details." >&2' ERR

# Step 1: Run Python Pipeline
echo ""
echo "[STEP 1/3] Executing Reproducibility Pipeline Stages..."
${PYTHON_CMD} run_all.py ${MODE} ${STAGES_ARG}

# Step 2: Compile LaTeX Manuscript
echo ""
echo "[STEP 2/3] Compiling LaTeX Manuscript (research_paper/main.tex)..."
pushd research_paper > /dev/null

echo "  Compiling via ${PDFLATEX_CMD} and ${BIBTEX_CMD}..."
${PDFLATEX_CMD} -interaction=nonstopmode main.tex > /dev/null 2>&1 || true
${BIBTEX_CMD} main > /dev/null 2>&1 || true
${PDFLATEX_CMD} -interaction=nonstopmode main.tex > /dev/null 2>&1 || true
${PDFLATEX_CMD} -interaction=nonstopmode main.tex > /dev/null 2>&1 || true

if [[ -f "main.pdf" ]]; then
  echo "  [SUCCESS] Generated main.pdf ($(wc -c < main.pdf) bytes)"
else
  echo "  [ERROR] main.pdf was not produced!"
  exit 1
fi
popd > /dev/null

# Step 3: Final Verification
echo ""
echo "[STEP 3/3] Running Post-Compilation Invariant Verification..."
${PYTHON_CMD} verify_paper.py

echo ""
echo "================================================================================"
echo "BUILD COMPLETED SUCCESSFULLY: Manuscript, tables, figures, and proofs verified!"
echo "PDF Output: research_paper/main.pdf"
echo "================================================================================"
exit 0
