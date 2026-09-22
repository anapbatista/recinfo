# Universidade de São Paulo – ICMC

## Departamento de Ciências de Computação

**Bacharelado em Ciências da Computação / Bacharelado em Ciências de Dados**  
**SCC0282 Recuperação de Informação – 2º Sem/2026**  
**Prof. Marcelo Manzato** (mmanzato@icmc.usp.br)

# Trabalho Prático 1

- **Divulgação:** 25/08/2026
- **Data de entrega:** 24/09/2026 até às 23:59

## Objetivo

O objetivo geral do projeto é desenvolver e avaliar um sistema de recuperação textual utilizando diferentes modelos clássicos de Recuperação de Informação apresentados em aula. Além disso, o projeto consiste em comparar diferentes estratégias de pré-processamento, representação, recuperação e parametrização por meio de métricas de avaliação.

## Metodologia

Será permitido utilizar APIs e bibliotecas específicas para tratamento de texto, leitura dos dados, tokenização, remoção de stopwords, stemming, cálculo de métricas e geração de gráficos. Entretanto, será de fundamental importância estar familiarizado com suas funcionalidades, de modo a compreender integralmente o código e as técnicas utilizadas no projeto.

O conjunto de dados adotado será o **Cranfield**, uma coleção clássica para avaliação de sistemas de Recuperação de Informação. A coleção contém documentos, consultas (*queries*) e julgamentos de relevância (*qrels*), permitindo avaliar os rankings produzidos pelos modelos.

A coleção pode ser acessada em:

- [ir_datasets – Cranfield](https://ir-datasets.com/cranfield.html)
- [Download alternativo dos arquivos originais: University of Glasgow – Cranfield Collection](https://www.dcs.gla.ac.uk/)

Acesso alternativo: [Hugging Face – irds/cranfield](https://huggingface.co/datasets/irds/cranfield)

Os julgamentos de relevância deverão ser utilizados exclusivamente para avaliação dos resultados, não podendo ser utilizados para definir, ajustar manualmente ou alterar diretamente o ranking produzido pelos modelos. Todos os experimentos deverão utilizar a mesma coleção de documentos, consultas e qrels.

## Requisitos

O projeto consiste em desenvolver e analisar os seguintes casos:

1. **Pré-processamento.** O sistema deverá realizar tokenização, normalização para letras minúsculas, tratamento de stopwords e stemming (ou técnica equivalente). Deverão ser comparadas, no mínimo, as seguintes configurações:
   - Sem stopwords e sem stemming;
   - Com remoção de stopwords;
   - Com stemming;
   - Com remoção de stopwords e stemming.

2. **Modelo Vetorial.** Deverá ser implementado o modelo vetorial utilizando ponderação de termos e similaridade do cosseno para produzir um ranking dos documentos para cada consulta. Os alunos deverão compreender e explicar como os documentos e consultas são representados e como o *score* de similaridade é calculado.

3. **Modelo Probabilístico.** Deverá ser implementado o BM25, produzindo um ranking dos documentos. Não é permitido utilizar diretamente uma implementação pronta que esconda completamente o cálculo do *score*. Bibliotecas podem ser utilizadas para tarefas auxiliares, mas os alunos deverão ser capazes de explicar e modificar a função implementada.

4. **Avaliação quantitativa.** Deverão ser calculadas, no mínimo, Precision@10, Recall@10 e MAP (*Mean Average Precision*). Métricas adicionais apresentadas em aula, como F1, MRR ou NDCG@10, poderão ser incluídas. Os resultados deverão ser mantidos por consulta e também agregados.

5. **Comparação entre modelos.** Deverá ser apresentada uma comparação quantitativa entre o Modelo Vetorial e o Modelo Probabilístico (BM25). Não será suficiente informar apenas qual modelo obteve a maior média; será necessário discutir em quais consultas ocorreram as maiores diferenças e apresentar hipóteses que expliquem esse comportamento.

6. **Análise por consulta.** Cada grupo deverá identificar:
   - Duas consultas em que o BM25 seja claramente superior ao Modelo Vetorial;
   - Duas consultas em que o Modelo Vetorial seja superior ao BM25;
   - Duas consultas em que ambos apresentem desempenho insatisfatório.

   Para cada caso deverão ser mostrados pelo menos os cinco primeiros documentos retornados, indicando quais são relevantes.

7. **Variação dos parâmetros do BM25.** Deverão ser avaliados, no mínimo:
   - \(k_1 \in \{0{,}5; 1{,}2; 2{,}0\}\)
   - \(b \in \{0; 0{,}75; 1\}\)

   Os grupos deverão comparar as configurações utilizando MAP e pelo menos uma outra métrica, discutir o efeito dos parâmetros e selecionar uma consulta em que a alteração de \(b\) provoque mudança perceptível no ranking.

8. **Modificação de consultas.** Cada grupo deverá selecionar cinco consultas e produzir manualmente uma versão alternativa de cada uma, por exemplo removendo ou acrescentando termos, utilizando sinônimos ou tornando a consulta mais específica ou genérica. As versões original e modificada deverão ser executadas com o Modelo Vetorial e o BM25, analisando as mudanças no Top-10.

9. **Análise de erros.** Deverão ser selecionados pelo menos dois documentos não relevantes que apareçam nas primeiras posições do ranking e um documento relevante que não apareça no Top-10. O grupo deverá investigar possíveis razões para esses comportamentos.

Para as métricas binárias (Precision, Recall e MAP), considere como relevante todo documento com grau de relevância maior ou igual a 1. Julgamentos com valor -1 e documentos não julgados deverão ser tratados como não relevantes. Caso NDCG seja utilizada, os graus positivos poderão ser mantidos como relevância graduada.

## Análise crítica dos resultados

A análise crítica é parte central do trabalho. Não será suficiente dizer que uma configuração apresentou x% de melhoria em relação a outra. É necessário investigar exemplos concretos e argumentar sobre por que os diferentes comportamentos ocorreram, relacionando os resultados aos conceitos estudados em aula, como frequência de termos, tamanho dos documentos, normalização, saturação da frequência no BM25, pré-processamento e características das consultas.

## Uso de ferramentas de Inteligência Artificial

Ferramentas de IA generativa podem ser utilizadas como apoio durante o desenvolvimento do projeto. Entretanto, todos os integrantes são responsáveis por compreender integralmente o código entregue, as fórmulas utilizadas, as decisões tomadas e os resultados obtidos.

Caso ferramentas de IA generativa tenham sido utilizadas, o relatório deverá conter uma breve seção denominada **“Uso de ferramentas de IA”**, indicando para quais atividades elas foram empregadas (por exemplo, apoio à programação, depuração, revisão textual ou explicação de conceitos). Não é necessário incluir o histórico completo das interações.

## Entrega

Deverão ser entregues:

1. O código-fonte completo do projeto;
2. Um arquivo README contendo:
   - Integrantes do grupo;
   - Instruções para instalação das dependências e execução;
   - Versão da linguagem e principais bibliotecas utilizadas;
   - Identificação e forma de obtenção da base de dados;
3. Os resultados completos dos experimentos, incluindo os resultados por consulta utilizados para produzir tabelas e gráficos;
4. Um relatório de desempenho em PDF de até 6 páginas (em Português ou Inglês), contendo as seguintes seções:
   - **Título/autores/filiação/email** (cabeçalho);
   - **Introdução** (contextualização, motivação e objetivo);
   - **Técnicas Utilizadas** (descrição das estratégias de recuperação e decisões de implementação);
   - **Avaliação** (dataset, consultas, qrels, métricas e configurações experimentais);
   - **Resultados Obtidos e Análise** (gráficos, tabelas, análise por consulta, parâmetros, reformulação de consultas e erros);
   - **Considerações finais** (principais conclusões obtidas a partir dos experimentos);
   - **Uso de ferramentas de IA**.

## Defesa do projeto

Além da entrega, poderá ser realizada uma breve avaliação individual. Qualquer integrante poderá ser solicitado a explicar uma parte do código ou uma fórmula, interpretar um resultado, justificar o score de um documento, prever o efeito da alteração de um parâmetro, executar novamente uma consulta ou realizar uma pequena modificação no código ou na configuração experimental.

## Observações finais

Os seguintes critérios de avaliação serão considerados durante a correção dos trabalhos:

1. Os alunos implementaram corretamente todas as funcionalidades exigidas na especificação?
2. A avaliação quantitativa foi realizada corretamente e os resultados são reprodutíveis?
3. O relatório entregue possui boa apresentação, organização e qualidade técnica?
4. Os alunos fizeram uma análise crítica dos casos estipulados, utilizando exemplos concretos para explicar os resultados?
5. Os integrantes demonstraram compreender o código, os modelos, as métricas e as decisões tomadas durante eventual defesa individual?

Como referência para composição da nota, serão considerados aproximadamente:

- **25%** para correção da implementação;
- **20%** para avaliação quantitativa e experimentos;
- **20%** para análise crítica das consultas e dos erros;
- **15%** para experimentos de parâmetros e pré-processamento;
- **10%** para qualidade técnica/apresentação do relatório;
- **10%** para compreensão individual/defesa.

## Referências e materiais de apoio

- MANNING, C. D.; RAGHAVAN, P.; SCHÜTZE, H. *Introduction to Information Retrieval*. Cambridge University Press, 2008. [Versão online](https://nlp.stanford.edu/IR-book/information-retrieval-book.html)
- ROBERTSON, S.; ZARAGOZA, H. *The Probabilistic Relevance Framework: BM25 and Beyond*. Foundations and Trends in Information Retrieval, 2009. [PDF](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- [ir_datasets – documentação da coleção Cranfield e exemplos de acesso aos documentos, consultas e qrels](https://ir-datasets.com/cranfield.html)
- [NLTK – documentação para tokenização, stopwords e stemming](https://www.nltk.org/)
- [scikit-learn – TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html) (material de apoio para ponderação de termos no Modelo Vetorial)
- [scikit-learn – cosine_similarity](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html)
- [ir_measures – documentação de métricas de avaliação em Recuperação de Informação](https://ir-measur.es/en/latest/)

Os materiais acima podem ser utilizados como apoio ao desenvolvimento. A implementação entregue deverá respeitar os requisitos desta especificação, principalmente quanto à compreensão do código e à implementação explícita do cálculo do BM25.

Dúvidas durante o desenvolvimento do trabalho podem ser sanadas com o professor por email.
