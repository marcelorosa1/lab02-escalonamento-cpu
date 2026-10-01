"""
Gera os graficos do Laboratorio 02 a partir do simulador.

Saidas (pasta graficos/):
  1_gantt_comparativo.png   - Gantt de FCFS, Round Robin (q=3) e SJF
  2_efeito_comboio.png      - espera de P2 atras de P1 no FCFS
  3_quantum_trocas.png      - trocas de contexto x tamanho do quantum
  4_medias_comparativo.png  - tempo medio de espera e retorno por algoritmo

Uso:
    pip install matplotlib
    python3 gerar_graficos.py
"""

import contextlib
import io
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from simulador_escalonador import (
    Processo,
    contar_trocas_contexto,
    simular_fcfs,
    simular_round_robin,
    simular_sjf,
)

PASTA = "graficos"
CORES = {"P1": "#4C72B0", "P2": "#DD8452", "P3": "#55A868", "P4": "#C44E52"}
WORKLOAD = [
    Processo("P1", 0, 8), Processo("P2", 1, 4),
    Processo("P3", 2, 9), Processo("P4", 3, 5),
]


def silencioso(funcao, *args, **kwargs):
    """Executa uma simulacao sem imprimir no terminal."""
    with contextlib.redirect_stdout(io.StringIO()):
        return funcao(*args, **kwargs)


def desenhar_gantt(ax, linha_tempo, titulo):
    for pid, inicio, fim in linha_tempo:
        ax.barh(0, fim - inicio, left=inicio, color=CORES[pid], edgecolor="black")
        ax.text((inicio + fim) / 2, 0, pid, ha="center", va="center",
                color="white", fontweight="bold")
    ax.set_title(titulo, loc="left")
    ax.set_yticks([])
    ax.set_xlim(0, 26)
    ax.set_xticks(sorted({0} | {fim for _, _, fim in linha_tempo}))
    ax.grid(axis="x", linestyle=":", alpha=0.6)


def grafico_gantt(resultados):
    fig, eixos = plt.subplots(3, 1, figsize=(10, 6))
    for ax, (nome, (procs, linha)) in zip(eixos, resultados.items()):
        media = sum(p.espera for p in procs) / len(procs)
        desenhar_gantt(ax, linha, f"{nome}  (espera media = {media:.2f} ms)")
        ax.set_xlabel("Tempo (ms)")
    fig.suptitle("Diagrama de Gantt - P1(0,8) P2(1,4) P3(2,9) P4(3,5)")
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA, "1_gantt_comparativo.png"), dpi=130)
    plt.close(fig)


def grafico_comboio(linha_fcfs):
    fig, ax = plt.subplots(figsize=(10, 3.2))
    linhas = {"P1": 1, "P2": 0}
    for pid, inicio, fim in linha_fcfs:
        if pid in linhas:
            ax.barh(linhas[pid], fim - inicio, left=inicio, color=CORES[pid],
                    edgecolor="black", label=f"{pid} executando")
    # Periodo em que P2 ja chegou e esta parado na fila de prontos
    ax.barh(0, 8 - 1, left=1, color="none", edgecolor=CORES["P2"], hatch="///",
            label="P2 esperando na fila (7 ms)")
    ax.annotate("P2 chega em t=1 ms", xy=(1, 0), xytext=(1, -0.75),
                arrowprops={"arrowstyle": "->"}, ha="center")
    ax.annotate("P2 so comeca em t=8 ms", xy=(8, 0), xytext=(9.5, -0.75),
                arrowprops={"arrowstyle": "->"}, ha="left")
    ax.set_yticks([0, 1], ["P2 (burst 4 ms)", "P1 (burst 8 ms)"])
    ax.set_ylim(-1.1, 1.6)
    ax.set_xlim(0, 13)
    ax.set_xticks(range(0, 14))
    ax.set_xlabel("Tempo (ms)")
    ax.set_title("Efeito comboio no FCFS: P2 (4 ms) espera 7 ms atras de P1 (8 ms)")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(axis="x", linestyle=":", alpha=0.6)
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA, "2_efeito_comboio.png"), dpi=130)
    plt.close(fig)


def grafico_quantum():
    quanta = list(range(1, 11)) + [50]
    trocas, esperas = [], []
    for q in quanta:
        procs, linha = silencioso(simular_round_robin, WORKLOAD, quantum=q)
        trocas.append(contar_trocas_contexto(linha))
        esperas.append(sum(p.espera for p in procs) / len(procs))

    rotulos = [str(q) for q in quanta]
    fig, ax1 = plt.subplots(figsize=(10, 4))
    barras = ax1.bar(rotulos, trocas, color="#4C72B0", label="Trocas de contexto")
    ax1.bar_label(barras)
    ax1.set_xlabel("Quantum (ms)")
    ax1.set_ylabel("Trocas de contexto")
    ax2 = ax1.twinx()
    ax2.plot(rotulos, esperas, color="#C44E52", marker="o", label="Espera media (ms)")
    ax2.set_ylabel("Espera media (ms)")
    ax1.set_title("Round Robin: efeito do tamanho do quantum")
    linhas1, nomes1 = ax1.get_legend_handles_labels()
    linhas2, nomes2 = ax2.get_legend_handles_labels()
    ax1.legend(linhas1 + linhas2, nomes1 + nomes2, loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA, "3_quantum_trocas.png"), dpi=130)
    plt.close(fig)
    return list(zip(quanta, trocas, esperas))


def grafico_medias(resultados):
    nomes = list(resultados)
    esperas = [sum(p.espera for p in r[0]) / len(r[0]) for r in resultados.values()]
    retornos = [sum(p.retorno for p in r[0]) / len(r[0]) for r in resultados.values()]
    x = range(len(nomes))
    fig, ax = plt.subplots(figsize=(8, 4))
    b1 = ax.bar([i - 0.2 for i in x], esperas, 0.4, label="Espera media", color="#4C72B0")
    b2 = ax.bar([i + 0.2 for i in x], retornos, 0.4, label="Retorno medio", color="#DD8452")
    ax.bar_label(b1, fmt="%.2f")
    ax.bar_label(b2, fmt="%.2f")
    ax.set_xticks(list(x), nomes)
    ax.set_ylabel("Tempo (ms)")
    ax.set_title("Comparativo de metricas por algoritmo")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA, "4_medias_comparativo.png"), dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(PASTA, exist_ok=True)
    resultados = {
        "FCFS": silencioso(simular_fcfs, WORKLOAD),
        "Round Robin (q=3)": silencioso(simular_round_robin, WORKLOAD, quantum=3),
        "SJF": silencioso(simular_sjf, WORKLOAD),
    }
    grafico_gantt(resultados)
    grafico_comboio(resultados["FCFS"][1])
    tabela = grafico_quantum()
    grafico_medias(resultados)

    print("Quantum | Trocas de contexto | Espera media")
    for q, t, e in tabela:
        print(f"{q:>7} | {t:>18} | {e:>9.2f} ms")
    print(f"\nGraficos salvos em {PASTA}/")
