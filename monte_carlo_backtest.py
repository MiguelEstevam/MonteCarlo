"""
Backtest + Monte Carlo para uma empresa fictícia.

1. Constrói dados históricos e um caminho de backtest.
2. Simula N_simulacoes trajetórias com N_periodos usando a mesma distribuição dos retornos.
3. Compara a média das simulações com o resultado do backtest.

Execução (N_simulacoes e N_periodos obrigatórios):
    python monte_carlo_backtest.py --N_simulacoes 10000 --N_periodos 36
"""

from __future__ import annotations

import argparse
import random
import statistics
from dataclasses import dataclass
from typing import Sequence


# ---------------------------------------------------------------------------
# Empresa / ideia de negócio
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Empresa:
    nome: str
    setor: str
    descricao: str
    valor_inicial: float
    retornos_mensais: tuple[float, ...]


EMPRESA = Empresa(
    nome="NimbusPay",
    setor="Fintech B2B (pagamentos para PME)",
    descricao=(
        "Plataforma de cobrança e antecipação de recebíveis. "
        "Série sintética de 36 meses: tração com volatilidade moderada "
        "e alguns meses negativos (churn, custo de aquisição)."
    ),
    valor_inicial=1_000_000.0,
    retornos_mensais=(
        0.018, 0.022, -0.005, 0.031, 0.012, 0.008,
        -0.012, 0.025, 0.019, 0.004, -0.008, 0.027,
        0.015, 0.011, -0.003, 0.034, 0.009, -0.015,
        0.021, 0.016, 0.006, -0.009, 0.028, 0.013,
        0.007, -0.011, 0.024, 0.017, 0.005, -0.006,
        0.029, 0.014, 0.010, -0.004, 0.020, 0.018,
    ),
)


# ---------------------------------------------------------------------------
# Distribuição (Normal ajustada aos retornos históricos — mesma família para MC)
# ---------------------------------------------------------------------------

@dataclass
class DistribuicaoRetornos:
    """Normal(μ, σ) estimada por máxima verossimilhança nos retornos mensais."""

    nome: str
    media: float
    desvio: float
    retornos_hist: tuple[float, ...]

    @classmethod
    def a_partir_historico(cls, retornos: Sequence[float]) -> DistribuicaoRetornos:
        ret = tuple(float(r) for r in retornos)
        if len(ret) < 2:
            raise ValueError("São necessários pelo menos 2 retornos históricos.")
        media = statistics.mean(ret)
        desvio = statistics.stdev(ret)
        return cls(
            nome="normal",
            media=media,
            desvio=desvio,
            retornos_hist=ret,
        )

    def amostrar(self, rng: random.Random) -> float:
        return rng.gauss(self.media, self.desvio)

    def resumo(self) -> str:
        return (
            f"Distribuicao: {self.nome}(media={self.media:.6f}, desvio={self.desvio:.6f}) | "
            f"media historica: {self.media:.4%} | desvio historico: {self.desvio:.4%}"
        )


def caminho_valor(valor_inicial: float, retornos: Sequence[float]) -> list[float]:
    valores = [valor_inicial]
    for r in retornos:
        valores.append(valores[-1] * (1.0 + r))
    return valores


def percentil(dados: list[float], p: float) -> float:
    if not dados:
        raise ValueError("Lista vazia.")
    ordenado = sorted(dados)
    k = (len(ordenado) - 1) * p / 100.0
    f = int(k)
    c = min(f + 1, len(ordenado) - 1)
    if f == c:
        return ordenado[f]
    return ordenado[f] + (k - f) * (ordenado[c] - ordenado[f])


# ---------------------------------------------------------------------------
# 1 — Backtest
# ---------------------------------------------------------------------------

def executar_backtest(empresa: Empresa) -> dict:
    valores = caminho_valor(empresa.valor_inicial, empresa.retornos_mensais)
    valor_final = valores[-1]
    retorno_total = valor_final / empresa.valor_inicial - 1.0
    return {
        "empresa": empresa,
        "n_periodos": len(empresa.retornos_mensais),
        "valores": valores,
        "valor_final": valor_final,
        "retorno_total": retorno_total,
    }


# ---------------------------------------------------------------------------
# 2 — Monte Carlo
# ---------------------------------------------------------------------------

def executar_monte_carlo(
    distribuicao: DistribuicaoRetornos,
    valor_inicial: float,
    n_simulacoes: int,
    n_periodos: int,
    seed: int = 42,
    guardar_caminhos: bool = True,
) -> dict:
    rng = random.Random(seed)
    valores_finais: list[float] = []
    caminhos: list[list[float]] = [] if guardar_caminhos else []

    for _ in range(n_simulacoes):
        valor = valor_inicial
        trajetoria = [valor_inicial] if guardar_caminhos else []
        for _ in range(n_periodos):
            r = distribuicao.amostrar(rng)
            valor *= 1.0 + r
            if guardar_caminhos:
                trajetoria.append(valor)
        valores_finais.append(valor)
        if guardar_caminhos:
            caminhos.append(trajetoria)

    return {
        "n_simulacoes": n_simulacoes,
        "n_periodos": n_periodos,
        "valores_finais": valores_finais,
        "caminhos": caminhos,
        "media_valores_finais": statistics.mean(valores_finais),
        "mediana_valores_finais": statistics.median(valores_finais),
        "p5_valores_finais": percentil(valores_finais, 5),
        "p95_valores_finais": percentil(valores_finais, 95),
    }


# ---------------------------------------------------------------------------
# 3 — Comparação
# ---------------------------------------------------------------------------

def comparar_resultados(backtest: dict, mc: dict, distribuicao: DistribuicaoRetornos) -> None:
    vb = backtest["valor_final"]
    vm = mc["media_valores_finais"]
    diff_abs = vm - vb
    diff_pct = (vm / vb - 1.0) if vb != 0 else float("nan")
    retorno_mc = vm / backtest["empresa"].valor_inicial - 1.0

    print("\n" + "=" * 72)
    print(f"Empresa: {backtest['empresa'].nome} — {backtest['empresa'].setor}")
    print(backtest["empresa"].descricao)
    print("=" * 72)
    print(distribuicao.resumo())
    print(
        f"\nMonte Carlo: N_simulacoes={mc['n_simulacoes']}, "
        f"N_periodos={mc['n_periodos']}"
    )
    print("\n--- Comparação (passo 3) ---")
    print(f"  Valor final backtest (passo 1):     {vb:>14,.2f} EUR")
    print(f"  Valor final media MC (passo 2):     {vm:>14,.2f} EUR")
    print(f"  Diferenca absoluta (media - back):  {diff_abs:>14,.2f} EUR")
    print(f"  Diferenca relativa:                 {diff_pct:>14.2%}")
    print(f"  Retorno total backtest:             {backtest['retorno_total']:>14.2%}")
    print(f"  Retorno total medio MC:             {retorno_mc:>14.2%}")
    print(f"  Mediana MC:                         {mc['mediana_valores_finais']:>14,.2f} EUR")
    print(
        f"  IC 90% (P5-P95):                    "
        f"[{mc['p5_valores_finais']:,.2f}, {mc['p95_valores_finais']:,.2f}] EUR"
    )
    print("=" * 72 + "\n")

    # Interpretação breve
    if abs(diff_pct) < 0.05:
        print(
            "Nota: backtest e média MC estão próximos — esperado quando "
            "N_periodos ~ historico e a distribuicao e a mesma (media, desvio dos retornos)."
        )
    else:
        print(
            "Nota: diferenca maior pode vir de N_periodos != tamanho do historico "
            "ou do caminho historico ser uma realizacao atipica da distribuicao."
        )
    print()


def plotar_opcional(backtest: dict, mc: dict, caminho: str = "resultado_monte_carlo.png") -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("(matplotlib não instalado — gráfico ignorado)")
        return

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    periodos_bt = list(range(len(backtest["valores"])))
    periodos_mc = list(range(mc["n_periodos"] + 1))

    ax0 = axes[0]
    amostra = min(200, len(mc["caminhos"]))
    indices = random.Random(0).sample(range(len(mc["caminhos"])), amostra)
    for i in indices:
        ax0.plot(periodos_mc, mc["caminhos"][i], color="steelblue", alpha=0.15, linewidth=0.8)
    ax0.plot(periodos_bt, backtest["valores"], color="crimson", linewidth=2.5, label="Backtest")
    ax0.axhline(mc["media_valores_finais"], color="darkgreen", linestyle="--", label="Média MC")
    ax0.set_xlabel("Período (meses)")
    ax0.set_ylabel("Valor (€)")
    ax0.set_title("Trajetórias MC vs backtest")
    ax0.legend()
    ax0.grid(True, alpha=0.3)

    ax1 = axes[1]
    ax1.hist(mc["valores_finais"], bins=50, density=True, alpha=0.6, color="steelblue")
    ax1.axvline(backtest["valor_final"], color="crimson", linewidth=2, label="Backtest")
    ax1.axvline(mc["media_valores_finais"], color="darkgreen", linestyle="--", label="Média MC")
    ax1.set_xlabel("Valor final (€)")
    ax1.set_title("Distribuição do valor final (simulações)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(caminho, dpi=120)
    plt.close()
    print(f"Gráfico guardado em: {caminho}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Backtest e Monte Carlo com a mesma distribuição de retornos."
    )
    parser.add_argument(
        "--N_simulacoes",
        type=int,
        required=True,
        help="Número de simulações Monte Carlo (obrigatório).",
    )
    parser.add_argument(
        "--N_periodos",
        type=int,
        required=True,
        help="Número de períodos por simulação (obrigatório).",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--grafico", action="store_true", help="Gerar PNG (requer matplotlib).")
    args = parser.parse_args()

    if args.N_simulacoes < 1 or args.N_periodos < 1:
        raise ValueError("N_simulacoes e N_periodos devem ser >= 1.")

    empresa = EMPRESA
    distribuicao = DistribuicaoRetornos.a_partir_historico(empresa.retornos_mensais)

    backtest = executar_backtest(empresa)
    mc = executar_monte_carlo(
        distribuicao=distribuicao,
        valor_inicial=empresa.valor_inicial,
        n_simulacoes=args.N_simulacoes,
        n_periodos=args.N_periodos,
        seed=args.seed,
        guardar_caminhos=args.grafico,
    )

    comparar_resultados(backtest, mc, distribuicao)

    if args.grafico:
        plotar_opcional(backtest, mc)


if __name__ == "__main__":
    main()
