#!/usr/bin/env bash
# Executa o simulador e gera os graficos, salvando as saidas em evidencias/.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p evidencias

python3 simulador_escalonador.py 1 50 | tee evidencias/saida_simulador.txt
python3 gerar_graficos.py | tee evidencias/saida_graficos.txt
