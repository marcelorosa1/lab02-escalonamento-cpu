"""
Laboratorio 02 - Simulacao de algoritmos de escalonamento de CPU.

Base: codigo do roteiro (FCFS e Round Robin), com os acrescimos:
  - SJF nao-preemptivo (para conferir a resolucao manual da Questao 3);
  - registro da linha do tempo de cada algoritmo (diagrama de Gantt em texto);
  - contagem de trocas de contexto (Questao 2);
  - quantum do Round Robin configuravel pela linha de comando.

Uso:
    python3 simulador_escalonador.py            # FCFS, RR (q=3) e SJF
    python3 simulador_escalonador.py 1 50       # tambem roda RR com q=1 e q=50
"""

import copy
import sys


class Processo:
    def __init__(self, pid, chegada, duracao):
        self.pid = pid
        self.chegada = chegada
        self.duracao = duracao
        self.restante = duracao
        self.finalizacao = 0
        self.espera = 0
        self.retorno = 0


# ---------------------------------------------------------------------------
# Funcoes auxiliares de relatorio
# ---------------------------------------------------------------------------

def contar_trocas_contexto(linha_tempo):
    """Conta quantas vezes a CPU passou de um processo para OUTRO processo.

    O primeiro despacho (CPU ociosa -> P1) nao e contado como troca.
    """
    trocas = 0
    for anterior, atual in zip(linha_tempo, linha_tempo[1:]):
        if anterior[0] != atual[0]:
            trocas += 1
    return trocas


def imprimir_gantt(linha_tempo):
    """Imprime o diagrama de Gantt em texto (3 caracteres = 1 ms)."""
    barra = "|"
    marcas = "0"
    for pid, inicio, fim in linha_tempo:
        largura = (fim - inicio) * 3
        barra += pid.center(largura - 1, "-") + "|"
        marcas += str(fim).rjust(largura)
    print("Gantt: " + barra)
    print("       " + marcas)


def imprimir_resumo(procs, linha_tempo):
    for p in sorted(procs, key=lambda x: x.pid):
        print(f"Proc {p.pid}: Fim={p.finalizacao}ms, Espera={p.espera}ms, Retorno={p.retorno}ms")

    media_esp = sum(p.espera for p in procs) / len(procs)
    media_ret = sum(p.retorno for p in procs) / len(procs)
    print(f"Tempo Medio de Espera:  {media_esp:.2f} ms")
    print(f"Tempo Medio de Retorno: {media_ret:.2f} ms")
    print(f"Trocas de contexto: {contar_trocas_contexto(linha_tempo)}")
    imprimir_gantt(linha_tempo)
    return media_esp, media_ret


# ---------------------------------------------------------------------------
# Algoritmos
# ---------------------------------------------------------------------------

def simular_fcfs(processos):
    procs = sorted(copy.deepcopy(processos), key=lambda x: x.chegada)
    tempo_atual = 0
    linha_tempo = []
    print("\n--- SIMULACAO FCFS ---")
    for p in procs:
        if tempo_atual < p.chegada:
            tempo_atual = p.chegada
        linha_tempo.append((p.pid, tempo_atual, tempo_atual + p.duracao))
        tempo_atual += p.duracao
        p.finalizacao = tempo_atual
        p.retorno = p.finalizacao - p.chegada
        p.espera = p.retorno - p.duracao

    imprimir_resumo(procs, linha_tempo)
    return procs, linha_tempo


def simular_round_robin(processos, quantum=3):
    procs = copy.deepcopy(processos)
    tempo_atual = 0
    fila, concluidos = [], []
    procs_ord = sorted(procs, key=lambda x: x.chegada)
    adicionados = set()
    linha_tempo = []

    def add_fila(t):
        for i, p in enumerate(procs_ord):
            if p.chegada <= t and i not in adicionados:
                fila.append(p)
                adicionados.add(i)

    add_fila(tempo_atual)
    print(f"\n--- SIMULACAO ROUND ROBIN (Quantum = {quantum}ms) ---")
    while fila:
        p_atual = fila.pop(0)
        tempo_exec = min(p_atual.restante, quantum)
        # Junta fatias consecutivas do mesmo processo (nao houve troca de contexto)
        if linha_tempo and linha_tempo[-1][0] == p_atual.pid:
            pid, inicio, _ = linha_tempo[-1]
            linha_tempo[-1] = (pid, inicio, tempo_atual + tempo_exec)
        else:
            linha_tempo.append((p_atual.pid, tempo_atual, tempo_atual + tempo_exec))
        tempo_atual += tempo_exec
        p_atual.restante -= tempo_exec
        add_fila(tempo_atual)
        if p_atual.restante > 0:
            fila.append(p_atual)
        else:
            p_atual.finalizacao = tempo_atual
            p_atual.retorno = p_atual.finalizacao - p_atual.chegada
            p_atual.espera = p_atual.retorno - p_atual.duracao
            concluidos.append(p_atual)

    imprimir_resumo(concluidos, linha_tempo)
    return concluidos, linha_tempo


def simular_sjf(processos):
    """SJF nao-preemptivo: entre os processos ja chegados, escolhe o de menor burst."""
    pendentes = sorted(copy.deepcopy(processos), key=lambda x: x.chegada)
    tempo_atual = 0
    concluidos = []
    linha_tempo = []
    print("\n--- SIMULACAO SJF (nao-preemptivo) ---")
    while pendentes:
        prontos = [p for p in pendentes if p.chegada <= tempo_atual]
        if not prontos:
            tempo_atual = pendentes[0].chegada
            continue
        p = min(prontos, key=lambda x: (x.duracao, x.chegada))
        pendentes.remove(p)
        linha_tempo.append((p.pid, tempo_atual, tempo_atual + p.duracao))
        tempo_atual += p.duracao
        p.finalizacao = tempo_atual
        p.retorno = p.finalizacao - p.chegada
        p.espera = p.retorno - p.duracao
        concluidos.append(p)

    imprimir_resumo(concluidos, linha_tempo)
    return concluidos, linha_tempo


if __name__ == "__main__":
    workload = [
        Processo("P1", 0, 8), Processo("P2", 1, 4),
        Processo("P3", 2, 9), Processo("P4", 3, 5)
    ]
    simular_fcfs(workload)
    simular_round_robin(workload, quantum=3)
    simular_sjf(workload)

    for q in sys.argv[1:]:
        simular_round_robin(workload, quantum=int(q))
