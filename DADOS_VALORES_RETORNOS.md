# NimbusPay — Documentação de valores e retornos

Documento de referência para o backtest e as simulações Monte Carlo do projeto `monte_carlo_backtest.py`.  
Todos os números de **backtest** e **estatísticas históricas** são determinísticos (derivados da série fixa). Os valores de **Monte Carlo** dependem de `N_simulacoes`, `N_periodos` e `seed`.

---

## Índice

1. [Perfil da empresa](#1-perfil-da-empresa)
2. [Convenções e fórmulas](#2-convenções-e-fórmulas)
3. [Série de retornos mensais](#3-série-de-retornos-mensais)
4. [Trajetória de valor (backtest)](#4-trajetória-de-valor-backtest)
5. [Estatísticas dos retornos históricos](#5-estatísticas-dos-retornos-históricos)
6. [Distribuição para Monte Carlo](#6-distribuição-para-monte-carlo)
7. [Resultados do backtest](#7-resultados-do-backtest)
8. [Monte Carlo — referência](#8-monte-carlo--referência)
9. [Comparação backtest vs média MC](#9-comparação-backtest-vs-média-mc)
10. [Execução e parâmetros](#10-execução-e-parâmetros)
11. [Glossário](#11-glossário)

---

## 1. Perfil da empresa

| Campo | Valor |
|-------|-------|
| **Nome** | NimbusPay |
| **Setor** | Fintech B2B (pagamentos para PME) |
| **Ideia de negócio** | Plataforma de cobrança e antecipação de recebíveis |
| **Moeda** | EUR |
| **Valor inicial** \(V_0\) | **1 000 000,00 EUR** |
| **Horizonte histórico** | 36 meses (períodos 1 a 36) |
| **Tipo de série** | Sintética (fictícia), para exercício de backtest / MC |

**Narrativa da série:** fase de tração com volatilidade moderada; meses negativos associados a churn ou aumento do custo de aquisição; maioria dos meses com crescimento positivo.

---

## 2. Convenções e fórmulas

### Retorno mensal simples

Para o mês \(t\) ( \(t = 1, \ldots, 36\) ):

\[
r_t = \frac{V_t - V_{t-1}}{V_{t-1}}
\qquad \Leftrightarrow \qquad
V_t = V_{t-1} \cdot (1 + r_t)
\]

- \(r_t\) em decimal: `0.018` = **+1,80 %**
- \(r_t < 0\): mês de queda do valor da empresa

### Retorno total do backtest (36 meses)

\[
R_{\text{total}} = \frac{V_{36}}{V_0} - 1
= \prod_{t=1}^{36}(1 + r_t) - 1
\]

### Retorno anualizado equivalente (referência)

Com 12 meses por ano e \(T = 36\) meses:

\[
R_{\text{anual}} \approx (1 + R_{\text{total}})^{12/T} - 1
\]

Para este backtest: \(R_{\text{total}} \approx 46{,}94\%\) → \(R_{\text{anual}} \approx 13{,}5\%\) (aproximação; assume composição mensal constante no horizonte).

### Monte Carlo

Em cada simulação \(s = 1, \ldots, N_{\text{simulacoes}}\):

1. Sorteia-se \(N_{\text{periodos}}\) retornos \( \tilde{r}_{s,1}, \ldots, \tilde{r}_{s,N_{\text{periodos}}} \) da **mesma** distribuição Normal estimada nos retornos históricos.
2. Aplica-se \( \tilde{V}_{s,t} = \tilde{V}_{s,t-1}(1 + \tilde{r}_{s,t}) \) com \( \tilde{V}_{s,0} = V_0 \).

---

## 3. Série de retornos mensais

Lista completa (fonte: `EMPRESA.retornos_mensais` em `monte_carlo_backtest.py`).

| Mês \(t\) | Retorno \(r_t\) | % | Mês \(t\) | Retorno \(r_t\) | % |
|----------:|----------------:|---:|----------:|----------------:|---:|
| 1 | 0,0180 | +1,80 % | 19 | 0,0210 | +2,10 % |
| 2 | 0,0220 | +2,20 % | 20 | 0,0160 | +1,60 % |
| 3 | −0,0050 | −0,50 % | 21 | 0,0060 | +0,60 % |
| 4 | 0,0310 | +3,10 % | 22 | −0,0090 | −0,90 % |
| 5 | 0,0120 | +1,20 % | 23 | 0,0280 | +2,80 % |
| 6 | 0,0080 | +0,80 % | 24 | 0,0130 | +1,30 % |
| 7 | −0,0120 | −1,20 % | 25 | 0,0070 | +0,70 % |
| 8 | 0,0250 | +2,50 % | 26 | −0,0110 | −1,10 % |
| 9 | 0,0190 | +1,90 % | 27 | 0,0240 | +2,40 % |
| 10 | 0,0040 | +0,40 % | 28 | 0,0170 | +1,70 % |
| 11 | −0,0080 | −0,80 % | 29 | 0,0050 | +0,50 % |
| 12 | 0,0270 | +2,70 % | 30 | −0,0060 | −0,60 % |
| 13 | 0,0150 | +1,50 % | 31 | 0,0290 | +2,90 % |
| 14 | 0,0110 | +1,10 % | 32 | 0,0140 | +1,40 % |
| 15 | −0,0030 | −0,30 % | 33 | 0,0100 | +1,00 % |
| 16 | 0,0340 | +3,40 % | 34 | −0,0040 | −0,40 % |
| 17 | 0,0090 | +0,90 % | 35 | 0,0200 | +2,00 % |
| 18 | −0,0150 | −1,50 % | 36 | 0,0180 | +1,80 % |

### Contagem por sinal

| Categoria | Quantidade | % dos 36 meses |
|-----------|------------|----------------|
| Meses positivos (\(r_t > 0\)) | 27 | 75,0 % |
| Meses negativos (\(r_t < 0\)) | 9 | 25,0 % |
| Meses nulos (\(r_t = 0\)) | 0 | 0,0 % |

### Extremos da série histórica

| Métrica | Valor | % |
|---------|------:|----:|
| **Mínimo** \(r_t\) | −0,0150 | −1,50 % (mês 18) |
| **Máximo** \(r_t\) | +0,0340 | +3,40 % (mês 16) |
| **Amplitude** | 0,0490 | 4,90 p.p. |

---

## 4. Trajetória de valor (backtest)

Evolução \(V_t\) com \(V_0 = 1\,000\,000\) EUR e retornos da secção 3.

| Período \(t\) | Retorno do mês | \(V_t\) (EUR) | Variação vs \(V_{t-1}\) (EUR) |
|-------------:|----------------|---------------:|------------------------------:|
| 0 | — | 1 000 000,00 | — |
| 1 | +1,80 % | 1 018 000,00 | +18 000,00 |
| 2 | +2,20 % | 1 040 396,00 | +22 396,00 |
| 3 | −0,50 % | 1 035 194,02 | −5 201,98 |
| 4 | +3,10 % | 1 067 285,03 | +32 091,01 |
| 5 | +1,20 % | 1 080 092,46 | +12 807,42 |
| 6 | +0,80 % | 1 088 733,19 | +8 640,74 |
| 7 | −1,20 % | 1 075 668,40 | −13 064,80 |
| 8 | +2,50 % | 1 102 560,11 | +26 891,71 |
| 9 | +1,90 % | 1 123 508,75 | +20 948,64 |
| 10 | +0,40 % | 1 128 002,78 | +4 494,03 |
| 11 | −0,80 % | 1 118 978,76 | −9 024,02 |
| 12 | +2,70 % | 1 149 191,19 | +30 212,43 |
| 13 | +1,50 % | 1 166 429,06 | +17 237,87 |
| 14 | +1,10 % | 1 179 259,77 | +12 830,72 |
| 15 | −0,30 % | 1 175 722,00 | −3 537,78 |
| 16 | +3,40 % | 1 215 696,54 | +39 974,55 |
| 17 | +0,90 % | 1 226 637,81 | +10 941,27 |
| 18 | −1,50 % | 1 208 238,25 | −18 399,57 |
| 19 | +2,10 % | 1 233 611,25 | +25 373,00 |
| 20 | +1,60 % | 1 253 349,03 | +19 737,78 |
| 21 | +0,60 % | 1 260 869,12 | +7 520,09 |
| 22 | −0,90 % | 1 249 521,30 | −11 347,82 |
| 23 | +2,80 % | 1 284 507,90 | +34 986,60 |
| 24 | +1,30 % | 1 301 206,50 | +16 698,60 |
| 25 | +0,70 % | 1 310 314,94 | +9 108,45 |
| 26 | −1,10 % | 1 295 901,48 | −14 413,46 |
| 27 | +2,40 % | 1 327 003,12 | +31 101,64 |
| 28 | +1,70 % | 1 349 562,17 | +22 559,05 |
| 29 | +0,50 % | 1 356 309,98 | +6 747,81 |
| 30 | −0,60 % | 1 348 172,12 | −8 137,86 |
| 31 | +2,90 % | 1 387 269,11 | +39 096,99 |
| 32 | +1,40 % | 1 406 690,88 | +19 421,77 |
| 33 | +1,00 % | 1 420 757,79 | +14 066,91 |
| 34 | −0,40 % | 1 415 074,76 | −5 683,03 |
| 35 | +2,00 % | 1 443 376,25 | +28 301,50 |
| 36 | +1,80 % | **1 469 357,02** | +25 980,77 |

### Marcos da trajetória

| Período | Valor (EUR) | Retorno acumulado desde \(V_0\) |
|--------:|------------:|--------------------------------:|
| 0 | 1 000 000,00 | 0,00 % |
| 6 | 1 088 733,19 | +8,87 % |
| 12 | 1 149 191,19 | +14,92 % |
| 18 | 1 208 238,25 | +20,82 % |
| 24 | 1 301 206,50 | +30,12 % |
| 30 | 1 348 172,12 | +34,82 % |
| 36 | **1 469 357,02** | **+46,94 %** |

### Maiores movimentos mensais em valor absoluto

| Tipo | Mês | Retorno | Variação (EUR) |
|------|----:|---------|---------------:|
| Maior ganho | 16 | +3,40 % | +39 974,55 |
| Maior perda | 18 | −1,50 % | −18 399,57 |

---

## 5. Estatísticas dos retornos históricos

Calculadas sobre os 36 retornos \(r_1, \ldots, r_{36}\) (desvio padrão amostral, `ddof=1`).

| Estatística | Valor decimal | Valor % |
|-------------|--------------:|--------:|
| Média \(\bar{r}\) | 0,010833 | **+1,0833 %** / mês |
| Desvio padrão \(s\) | 0,013388 | 1,3388 % / mês |
| Mínimo | −0,015000 | −1,50 % |
| Máximo | +0,034000 | +3,40 % |
| Coef. variação \(s / \bar{r}\) | 1,236 | — |
| Soma dos retornos simples* | 0,390000 | 39,00 % |

\* *A soma dos retornos simples não é igual ao retorno composto total; o retorno total correto usa o produto \((1+r_t)\).*

### Retorno composto vs soma simples

| Medida | Valor |
|--------|------:|
| Retorno total composto \(V_{36}/V_0 - 1\) | **+46,94 %** |
| Soma \(\sum r_t\) (aproximação linear) | +39,00 % |

---

## 6. Distribuição para Monte Carlo

Ajuste usado no passo 2 (mesma família para todas as simulações):

| Parâmetro | Símbolo | Valor |
|-----------|---------|------:|
| Família | — | Normal |
| Média | \(\mu\) | 0,010833 (+1,0833 % / mês) |
| Desvio | \(\sigma\) | 0,013388 (1,3388 % / mês) |
| Estimação | MLE / momentos | \(\mu = \bar{r}\), \(\sigma = s\) |

**Amostragem:** \(\tilde{r} \sim \mathcal{N}(\mu, \sigma^2)\) em cada mês simulado (implementação: `random.gauss`).

**Nota:** o backtest usa o **caminho histórico fixo**; o MC usa **sorteios independentes** com \(\mu\) e \(\sigma\) da história. O caminho histórico é uma única realização; a média de muitas simulações aproxima o valor esperado sob a Normal.

---

## 7. Resultados do backtest

| Métrica | Valor |
|---------|------:|
| Valor inicial \(V_0\) | 1 000 000,00 EUR |
| Valor final \(V_{36}\) | **1 469 357,02 EUR** |
| Ganho absoluto | +469 357,02 EUR |
| Retorno total \(R_{\text{total}}\) | **+46,94 %** |
| Fator de crescimento | 1,4694× |
| Número de períodos | 36 meses |

---

## 8. Monte Carlo — referência

Configuração de referência (reprodutível com o script):

```text
N_simulacoes = 10 000
N_periodos   = 36
seed         = 42
valor_inicial = 1 000 000 EUR
```

### Estatísticas do valor final \(\tilde{V}_{s,N}\) (10 000 simulações)

| Métrica | Valor (EUR) | Retorno vs \(V_0\) |
|---------|------------:|-------------------:|
| **Média** | 1 474 313,55 | +47,43 % |
| **Mediana** | 1 469 366,71 | +46,94 % |
| **P5** (5.º percentil) | 1 288 857,88 | +28,89 % |
| **P95** (95.º percentil) | 1 678 003,64 | +67,80 % |
| Amplitude P5–P95 | 389 145,76 | — |

A mediana MC muito próxima do valor final do backtest é coerente: ambas refletem 36 meses de composição; a média MC é ligeiramente superior por assimetria da distribuição do valor final.

---

## 9. Comparação backtest vs média MC

Referência: `N_simulacoes = 10 000`, `N_periodos = 36`, `seed = 42`.

| Indicador | Backtest (histórico) | Monte Carlo (média) | Diferença |
|-----------|---------------------:|--------------------:|----------:|
| Valor final | 1 469 357,02 EUR | 1 474 313,55 EUR | +4 956,53 EUR |
| Retorno total | +46,94 % | +47,43 % | +0,49 p.p. |
| Diferença relativa (média / backtest − 1) | — | — | **+0,34 %** |

### Interpretação

| Situação | Leitura |
|----------|---------|
| `N_periodos = 36` e mesma \((\mu, \sigma)\) | Backtest e média MC tendem a ficar próximos (ordem de grandeza igual). |
| `N_periodos ≠ 36` | Valor esperado MC escala com o horizonte; comparação direta com \(V_{36}\) deixa de ser 1:1. |
| Backtest vs mediana MC | Mediana ≈ backtest nesta referência (~46,94 % de retorno). |
| Backtest vs P5–P95 | O histórico é **um** caminho; o IC mostra dispersão possível sob a Normal. |

---

## 10. Execução e parâmetros

### Comando

```powershell
cd c:\UCL\PO
python monte_carlo_backtest.py --N_simulacoes 10000 --N_periodos 36
```

### Argumentos

| Argumento | Obrigatório | Descrição |
|-----------|:-----------:|-----------|
| `--N_simulacoes` | Sim | Número de trajetórias independentes |
| `--N_periodos` | Sim | Meses simulados em cada trajetória |
| `--seed` | Não (default: 42) | Semente do gerador aleatório |
| `--grafico` | Não | Gera `resultado_monte_carlo.png` (requer matplotlib) |

### Ficheiros do projeto

| Ficheiro | Função |
|----------|--------|
| `monte_carlo_backtest.py` | Código: backtest, MC, comparação |
| `DADOS_VALORES_RETORNOS.md` | Este documento |
| `requirements.txt` | Dependências opcionais (matplotlib) |

### Atualizar este documento

Se alterar `EMPRESA.retornos_mensais` ou `valor_inicial` no Python:

1. Recalcule a tabela da secção 4 (ou execute o script e exporte).
2. Atualize secções 5, 7 e, se aplicável, 8–9 com nova corrida MC.

---

## 11. Glossário

| Termo | Definição |
|-------|-----------|
| **Retorno simples** | Variação percentual do valor num único período: \((V_t - V_{t-1})/V_{t-1}\). |
| **Backtest** | Aplicação sequencial dos retornos **históricos** observados (caminho único). |
| **Monte Carlo** | Muitas trajetórias com retornos **sorteados** da mesma distribuição estimada. |
| **\(N_{\text{simulacoes}}\)** | Quantas trajetórias independentes são geradas. |
| **\(N_{\text{periodos}}\)** | Quantos meses dura cada trajetória simulada. |
| **Valor final** | \(V\) após o último período (mês 36 no histórico, ou `N_periodos` no MC). |
| **P5 / P95** | Percentis 5 e 95 da distribuição simulada do valor final (faixa central ~90 %). |

---

*Última sincronização numérica com `monte_carlo_backtest.py` (EMPRESA NimbusPay, 36 meses, MC referência 10 000 × 36, seed 42).*
