# Trabalho Prático 1 — Recuperação de Informação (SCC0282)

Sistema de recuperação textual sobre a coleção **Cranfield** que implementa e compara o **Modelo Vetorial** (TF-IDF + similaridade do cosseno) e o **BM25** (score implementado manualmente). O projeto avalia quatro configurações de pré-processamento, calcula métricas por consulta e agregadas (P@10, R@10, F1@10, MAP, MRR e NDCG@10), varia os parâmetros $k_1$ e $b$ do BM25, testa versões modificadas de consultas e analisa erros de recuperação.

## Integrantes

- Ana Paula de Abreu Batista — nº USP 12688424

## Estrutura do repositório

| Caminho | Conteúdo |
|---|---|
| `trabalho_pratico_recinfo.ipynb` | Código-fonte completo (notebook, já executado, com todas as saídas) |
| `resultados/` | Resultados dos experimentos: CSVs por consulta e agregados, e gráficos (gerados pelo notebook) |
| `relatorio.tex` / `relatorio.pdf` | Relatório de desempenho (fonte LaTeX e PDF) |
| `requirements.txt` | Dependências com as versões usadas |
| `Trabalho_Pratico_1_RI_2026.pdf` | Especificação do trabalho |

## Versões utilizadas

Os resultados do repositório foram gerados com:

| Componente | Versão |
|---|---|
| Python | 3.13.13 |
| ir-datasets | 0.6.3 |
| nltk | 3.10.3 |
| scikit-learn | 1.9.1 |
| pandas | 3.0.6 |
| numpy | 2.5.3 |
| matplotlib | 3.11.2 |
| nbconvert / ipykernel (execução do notebook) | 7.17.1 / 7.3.0 |

O notebook imprime as versões na segunda célula de código, então qualquer nova execução registra o ambiente usado. Todos os passos são determinísticos, sem aleatoriedade, e duas execuções produzem os mesmos números.

## Instalação

Requer Python 3.11 ou superior (exigência do pandas 3 e do numpy 2.5; testado com 3.13).

```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

## Execução

A primeira execução precisa de internet para baixar a coleção Cranfield (cerca de 500 kB) e a lista de stopwords do NLTK.

**Linha de comando** (executa o notebook inteiro e grava as saídas nele mesmo; leva cerca de 4 minutos):

```bash
jupyter nbconvert --to notebook --execute --inplace trabalho_pratico_recinfo.ipynb
```

**Editor:** abra `trabalho_pratico_recinfo.ipynb` no VS Code ou no Jupyter, selecione o ambiente `.venv` como kernel e execute todas as células.

**Google Colab:** use o botão *Open in Colab* no topo do notebook. A primeira célula de código instala as dependências.

Em qualquer uma das opções, os CSVs e gráficos são gravados em `resultados/`.

## Base de dados

- **Coleção:** Cranfield — 1.400 documentos (resumos de artigos de aeronáutica), 225 consultas e 1.837 julgamentos de relevância.
- **Obtenção:** automática, pela biblioteca [`ir_datasets`](https://ir-datasets.com/cranfield.html), com `ir_datasets.load("cranfield")`. Na primeira execução, a biblioteca baixa o arquivo original `cran.tar.gz` da Universidade de Glasgow (<http://ir.dcs.gla.ac.uk/resources/test_collections/cran/>) e o guarda em cache em `~/.ir_datasets`. Nenhum arquivo de dados precisa ser baixado manualmente. Também há uma cópia no Hugging Face: [irds/cranfield](https://huggingface.co/datasets/irds/cranfield).
- **Relevância:** para as métricas binárias, é relevante todo documento com grau ≥ 1. Julgamentos -1 e documentos não julgados contam como não relevantes. Na escala original de Cleverdon (arquivo `cranqrel.readme` da coleção), **1 = resposta completa** e **4 = interesse mínimo**. Por isso, o NDCG@10 usa o ganho `5 − grau`. A documentação do `ir_datasets` descreve a escala na ordem inversa, mas a biblioteca não transforma os valores do arquivo original.

## Resultados (`resultados/`)

| Arquivo | Conteúdo |
|---|---|
| `resultados_por_consulta.csv` | P@10, R@10, F1@10, AP, RR e NDCG@10 por consulta, para os 2 modelos × 4 pré-processamentos |
| `resultados_agregados.csv` | Médias das métricas acima por modelo e pré-processamento |
| `ablacao_titulo_por_consulta.csv` | AP por consulta indexando só o campo `text` (título 1×) |
| `analise_por_consulta_ambos_modelos.csv` | Vetorial vs. BM25 por consulta (pré-processamento `both`) |
| `posicao_documento_fonte.csv` | Posição, em cada modelo, do documento com julgamento -1 de cada consulta |
| `resultados_variacao_parametros_bm25.csv` | MAP, P@10 e NDCG@10 das 9 combinações de $k_1$ e $b$ |
| `resultados_variacao_parametros_bm25_por_consulta.csv` | As mesmas métricas por consulta |
| `resultados_modificacao_consultas.csv` | Consultas originais e modificadas: AP, P@10, sobreposição e mudanças no Top 10 |
| `falsos_positivos_bm25.csv`, `falsos_negativos_bm25.csv` | Candidatos da análise de erros (BM25, $k_1=2.0$, $b=0.75$) |
| `grafico_*.png` | Gráficos: MAP por pré-processamento, comparação de métricas, diferença de AP por consulta e heatmap de $k_1 \times b$ |

## Relatório

O relatório está em `relatorio.pdf`. Para recompilar a partir de `relatorio.tex`, use `pdflatex relatorio.tex` (duas vezes) ou o Overleaf. As figuras são lidas de `resultados/`.
