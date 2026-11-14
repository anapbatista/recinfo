# Trabalho Prático 2 — Recuperação de Informação (SCC0282)

Sistema de Recuperação de Informação sobre a coleção **NFCorpus** (benchmark BEIR) que combina busca lexical e busca semântica. O pipeline completo é:

`documentos → pré-processamento e indexação → recuperação lexical + recuperação semântica → busca híbrida (RRF) → reranking → seleção de contexto → LLM → resposta (RAG)`

O projeto implementa o índice invertido e o BM25 do zero, correção ortográfica (k-gramas, Jaccard e distância de edição), busca semântica com bi-encoder, fusão por Reciprocal Rank Fusion, reranking com cross-encoder e um experimento sem RAG × com RAG, com avaliação quantitativa e análise por consulta.

## Integrantes

- Ana Paula de Abreu Batista — nº USP 12688424
- Italo Carlos Martins Bresciani — nº USP 15461782

## Estrutura da entrega

| Caminho | Conteúdo |
|---|---|
| `trabalho_pratico_2.ipynb` | Código-fonte completo (notebook único, já executado, com saídas e análises) |
| `resultados/` | Arquivos CSV padronizados, arquivos de apoio da avaliação do RAG e gráficos |
| `relatorio.tex` / `relatorio.pdf` | Relatório de desempenho (fonte LaTeX e PDF) |
| `requirements.txt` | Dependências com as versões usadas |
| `README.md` | Este arquivo |
| `Trabalho_Pratico_2_RI_2026.pdf` | Especificação do trabalho |

As pastas `dados/` (coleção), `artefatos/` (embeddings dos documentos e scores do cross-encoder) e `modelos/` (arquivo da LLM) **não são entregues**: o notebook as recria na primeira execução (ver "Execução").

## Modelos e configurações

| Componente | Escolha |
|---|---|
| Pré-processamento | minúsculas, tokenização `\w+`, remoção de stopwords (NLTK, inglês) e stemming de Porter; configuração escolhida no `dev` |
| Modelo lexical | **BM25** ($k_1 = 1{,}2$, $b = 0{,}75$) sobre índice invertido implementado do zero |
| Correção ortográfica | bigramas de caracteres, limiar de Jaccard 0,4 e distância de Levenshtein; parâmetros escolhidos no `dev` |
| Modelo de embeddings | **`sentence-transformers/all-MiniLM-L6-v2`** (bi-encoder, 384 dimensões, cosseno, entrada de 256 tokens); escolhido no `dev` |
| Busca híbrida | Reciprocal Rank Fusion dos 100 primeiros de cada sistema, $k = 10$ (escolhido no `dev`) |
| Modelo de reranking | **`cross-encoder/ms-marco-MiniLM-L6-v2`** sobre os 50 primeiros do híbrido (entrada de 512 tokens); escolhido no `dev` |
| LLM (RAG) | **`Qwen2.5-3B-Instruct`** (GGUF `q4_k_m`), execução local em CPU com `llama-cpp-python`; temperatura 0, seed 42, até 400 tokens gerados; respostas em inglês; sem custo |

As revisões (commits) dos modelos no Hugging Face estão fixadas no notebook.

## Hardware e versões utilizadas

Os resultados entregues foram gerados em um notebook com processador Intel Core i5-1334U (12 threads), 16 GB de RAM, **sem GPU**, em Linux (Ubuntu).

| Componente | Versão |
|---|---|
| Python | 3.12.3 |
| numpy / pandas | 2.5.4 / 3.1.1 |
| nltk | 3.10.4 |
| torch (CPU) | 2.15.0 |
| transformers / sentence-transformers | 5.23.0 / 6.3.0 |
| llama-cpp-python | 0.3.36 |
| ir-measures | 0.4.3 |
| matplotlib | 3.11.2 |
| nbconvert / ipykernel (execução do notebook) | 7.17.2 / 7.4.0 |

O notebook imprime as versões na primeira célula de código, então qualquer nova execução registra o ambiente usado.

## Instalação

Requer Python 3.11 ou superior.

```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# Opcional, em máquina sem GPU (instala o PyTorch só de CPU, bem menor):
pip install torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu

pip install -r requirements.txt
```

## Execução

Há um único notebook. As células devem ser executadas na ordem, de cima para baixo.

**Linha de comando** (executa o notebook inteiro e grava as saídas nele mesmo):

```bash
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 trabalho_pratico_2.ipynb
```

**Editor:** abra `trabalho_pratico_2.ipynb` no VS Code ou no Jupyter, selecione o ambiente `.venv` como kernel e execute todas as células.

**O que a primeira execução faz** (precisa de internet):

1. baixa o NFCorpus (2,4 MB) do repositório oficial do BEIR para `dados/`;
2. baixa do Hugging Face os dois bi-encoders e os dois cross-encoders avaliados (cerca de 90 MB cada, ou menos) e o arquivo da LLM (2,1 GB) para `modelos/`;
3. calcula os embeddings dos documentos e os scores do cross-encoder e os grava em `artefatos/`.

**Tempo aproximado em CPU** (no hardware acima): cerca de 10 minutos para os embeddings dos dois bi-encoders, 60 minutos para o reranking (dois modelos no `dev` e o escolhido no `test`) e 20 minutos para as 20 respostas da LLM. Com GPU, os modelos do Sentence Transformers a usam automaticamente e essas etapas ficam muito mais rápidas.

**Reexecuções** levam poucos minutos, porque os embeddings, os scores do cross-encoder e as respostas da LLM são reaproveitados do disco. Para refazer tudo do zero:

- apague a pasta `artefatos/` para recalcular os embeddings e o reranking (os tempos registrados também são medidos de novo);
- apague `resultados/rag_respostas.json` para gerar as respostas da LLM de novo. Atenção: as notas da avaliação humana se referem aos textos das respostas; se alguma resposta mudar, o notebook avisa e ela precisa ser avaliada novamente.

## Base de dados

- **Coleção:** NFCorpus, na versão do BEIR — 3.633 documentos (títulos e resumos de artigos da área médica e de nutrição) e 3.237 consultas no total.
- **Obtenção:** automática, a partir do arquivo oficial <https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/nfcorpus.zip>, que contém `corpus.jsonl`, `queries.jsonl` e os qrels.
- **Splits:** as consultas de cada conjunto são as que têm julgamentos em `qrels/dev.tsv` (324 consultas) e `qrels/test.tsv` (323 consultas). O `dev` é usado para todas as escolhas de configuração; o `test`, apenas na avaliação final.
- **Documentos:** representados por `title + " " + text` em todos os sistemas.
- **Relevância:** graus 1 e 2 nos qrels. Para P@10, R@10 e MAP@10, é relevante todo documento com grau maior que zero; o NDCG@10 usa os graus com ganho linear.

## Resultados (`resultados/`)

| Arquivo | Conteúdo |
|---|---|
| `results_lexical.csv`, `results_semantic.csv`, `results_hybrid.csv`, `results_reranking.csv` | 100 primeiros documentos de cada consulta do `test`: `query_id`, `doc_id`, `rank`, `score`, `relevance` |
| `metrics_per_query.csv` | `query_id`, `model`, `P10`, `R10`, `AP10`, `NDCG10` dos quatro sistemas (a média de `AP10` é o MAP@10) |
| `typo_experiment.csv` | Experimento de tolerância a erros: consulta original, com erro e corrigida, tipo de erro e NDCG@10 nas três condições (inclui a parte opcional com o sistema semântico) |
| `rag_experiment.csv` | Experimento sem RAG × com RAG: `query_id`, `query`, `condition` (A ou B), `context_doc_ids`, `prompt`, `answer`, as quatro notas e as justificativas |
| `rag_respostas.json` | Respostas geradas pela LLM (com prompt, número de tokens e tempo) |
| `avaliacao_rag_cega.csv` | Planilha de avaliação com as 20 respostas embaralhadas, sem a condição |
| `avaliacao_rag_preenchida.csv` | A mesma planilha com as notas e justificativas preenchidas |
| `grafico_*.png` | Gráficos gerados pelo notebook |

Observações sobre os arquivos de ranking:

- `results_lexical.csv` pode ter menos de 100 linhas por consulta (ou nenhuma), quando poucos documentos contêm os termos da consulta.
- Em `results_reranking.csv`, o `score` das posições 1 a 50 é o do cross-encoder. Nas posições seguintes, que mantêm a ordem do híbrido, é o score do RRF menos 100, para que o arquivo continue ordenado por `score`.

Resumo no conjunto `test` (323 consultas):

| Sistema | P@10 | R@10 | MAP@10 | NDCG@10 |
|---|---|---|---|---|
| Lexical (BM25) | 0,2393 | 0,1533 | 0,1218 | 0,3280 |
| Semântico | 0,2433 | 0,1550 | 0,1108 | 0,3167 |
| Híbrido (RRF) | 0,2604 | 0,1754 | 0,1353 | 0,3549 |
| Híbrido + reranking | 0,2511 | 0,1674 | 0,1389 | 0,3564 |

## Relatório

O relatório está em `relatorio.pdf`. Para recompilar a partir de `relatorio.tex`, use `pdflatex relatorio.tex` (duas vezes) ou o Overleaf. As figuras são lidas de `resultados/`.

## Reprodutibilidade

- Todos os sorteios usam seed 42, e as revisões dos modelos estão fixadas.
- Rankings e métricas são determinísticos: empates de score são desfeitos pelo `doc_id`.
- A LLM usa temperatura 0 (decodificação gulosa). Em outro hardware, pequenas diferenças numéricas podem alterar algumas palavras das respostas.
- Os tempos medidos dependem da máquina e da carga no momento da execução.
