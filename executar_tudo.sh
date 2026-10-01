#!/usr/bin/env bash
# Executa o simulador e gera os graficos, salvando as saidas em evidencias/.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p evidencias

{
    echo "Data......: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "Sistema...: $(. /etc/os-release 2>/dev/null && echo "$PRETTY_NAME" || uname -s)"
    echo "Kernel....: $(uname -r)"
    echo "Arquitetura: $(uname -m)"
    echo "Python....: $(python3 --version | cut -d' ' -f2)"
    echo "matplotlib: $(python3 -c 'import matplotlib; print(matplotlib.__version__)')"
} > evidencias/ambiente.txt

python3 simulador_escalonador.py 1 50 | tee evidencias/saida_simulador.txt
python3 gerar_graficos.py | tee evidencias/saida_graficos.txt
