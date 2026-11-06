# ⚡ NLP Playground: Como o Google e as IAs Entendem o Português? — Feira de Extensão (SCC0282)

Aplicação interativa em **Streamlit** desenvolvida para apresentar o tema **Part-of-Speech Tagging (Etiquetagem Morfossintática)** e seu papel em **Recuperação de Informação** com uma linguagem moderna, dinâmica e acessível para **estudantes de Ensino Médio (16–18 anos)** e público geral na Feira de Extensão da USP.

## 👥 Integrantes do Grupo
- **Ana Paula de Abreu Batista** — nº USP 12688424
- **Italo Carlos Martins Bresciani** — nº USP 15461782

---

## 🎯 O que o visitante experimenta na apresentação?

A interface funciona como um **Playground interativo de PLN e Busca**, usando exemplos do cotidiano jovem (games, música, vídeos curtos, gírias da internet, esportes e finanças):

1. **🔍 1. Raio-X da Frase (Analisador em Tempo Real):**
   - O visitante digita qualquer frase (ou escolhe exemplos com ambiguidades e gírias como *"O time inteiro tankou a partida"*) e vê como o modelo classifica cada palavra em **Substantivo**, **Verbo**, **Adjetivo**, **Advérbio**, **Pronome** ou **Conector / Funcional**.
   - Mostra **como o contexto sintático definiu cada etiqueta** e o que realmente entra no **Índice Invertido** de um buscador (`(lema, classe)`) vs. o que é filtrado como *Stop Word*.

2. **🎭 2. Ambiguidade & Palavras Gêmeas (Polissemia e Homografia):**
   - Compara lado a lado palavras idênticas que mudam de classe e de lema conforme o contexto:
     - **«jogo»**: *"Toda sexta eu **jogo** bola"* (`Verbo` → lema `jogar`) vs. *"Esse **jogo** tem gráficos absurdos"* (`Substantivo` → lema `jogo`)
     - **«rio»**: *"Eu **rio** demais com esses vídeos"* (`Verbo` → lema `rir`) vs. *"Travessia de caiaque pelo **rio**"* (`Substantivo` → lema `rio`)
     - Além de **«canto»**, **«banco»**, **«manga»** e **«nada»**, mostrando por que um *Stemmer* cego falha onde a **Lematização Contextualizada com POS Tagging** acerta.
   - Inclui um **Teste de Fogo** para o visitante usar a mesma palavra duas vezes na mesma frase com sentidos diferentes.

3. **🚀 3. Simulador de Motor de Busca (Literal/Stemmer vs. Busca com POS):**
   - Compara na prática uma **Busca Sem POS Tagging** (que traz falsos positivos por homografia) com a **Busca Inteligente com POS Tagging**, sobre uma coleção de 8 textos de cultura pop, games, música, tecnologia, esportes e cotidiano.

4. **⚡ 4. Desafio: Você vs. IA (Quiz de Contexto):**
   - Quiz rápido com desafios de desambiguação e neologismos/gírias da internet para engajar os visitantes no estande.

5. **⚙️ 5. Por Trás do Código (`spaCy` + `NLTK`):**
   - Aba técnica exibindo as *Universal POS Tags* (`UPOS`), dependências sintáticas (`dep_`), feições morfológicas (`morph`) do **spaCy (`pt_core_news_sm`)** e a comparação direta com o radical gerado pelo `RSLPStemmer` do **NLTK**.

---

## 🚀 Como executar

```powershell
# 1. Ativar o ambiente virtual
.\feiraextensao\.venv\Scripts\Activate.ps1

# 2. Executar o aplicativo no Streamlit
streamlit run .\feiraextensao\app.py
```
