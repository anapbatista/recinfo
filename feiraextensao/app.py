"""
Aplicação interativa em Streamlit para a Feira de Extensão — SCC0282 (Recuperação de Informação).
Tema: Part-of-Speech Tagging & Recuperação de Informação
Público-alvo: Estudantes de Ensino Médio (16–18 anos) e público visitante da feira.
"""

from __future__ import annotations

import html
import importlib
import re
import streamlit as st

import nlp_engine

importlib.reload(nlp_engine)
from nlp_engine import (
    COLECAO_DOCUMENTOS,
    POS_INFO,
    TokenAnalisado,
    analisar_frase,
    buscar_documentos,
)


# ============================================================================
# CONFIGURAÇÃO DA PÁGINA E ESTILO VISUAL (MODERNO, DINÂMICO, 16–18 ANOS)
# ============================================================================

st.set_page_config(
    page_title="NLP Playground — Como a IA Entende o Português? | USP",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2.5rem;
        max-width: 1220px;
    }

    /* Cabeçalho estilo AI Playground moderno */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 55%, #312E81 100%);
        color: #F8FAFC;
        padding: 1.7rem 2.1rem;
        border-radius: 18px;
        border: 1px solid #334155;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.18);
        margin-bottom: 1.3rem;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.25);
        color: #A5B4FC;
        border: 1px solid rgba(129, 140, 248, 0.4);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 3px 10px;
        border-radius: 999px;
        margin-bottom: 8px;
    }
    .hero-banner h1 {
        color: #FFFFFF !important;
        font-size: 2.1rem !important;
        margin: 0 0 0.4rem 0 !important;
        font-weight: 800 !important;
    }
    .hero-banner p {
        color: #CBD5E1 !important;
        font-size: 1.05rem !important;
        margin: 0 !important;
    }

    /* Palco de tokens etiquetados */
    .token-stage {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.25rem;
        margin: 0.9rem 0;
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        align-items: stretch;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }
    .token-chip {
        display: inline-flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 10px 14px;
        border-radius: 12px;
        border: 2px solid;
        min-width: 88px;
        text-align: center;
        transition: transform 0.12s ease, box-shadow 0.12s ease;
    }
    .token-chip:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 14px rgba(0,0,0,0.08);
    }
    .token-word {
        font-size: 1.28rem;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 5px;
    }
    .token-pos {
        font-size: 0.78rem;
        font-weight: 700;
        padding: 2px 9px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.88);
        margin-bottom: 4px;
    }
    .token-lemma {
        font-size: 0.74rem;
        opacity: 0.88;
        font-family: monospace;
    }
    .ambig-badge {
        margin-top: 4px;
        font-size: 0.68rem;
        background: #FEF08A;
        color: #854D0E;
        padding: 1px 7px;
        border-radius: 999px;
        font-weight: 700;
        border: 1px solid #FACC15;
    }

    /* Cartões de explicação e busca */
    .info-card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        border: 1px solid #E2E8F0;
        border-left: 6px solid #4F46E5;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
        margin-bottom: 0.75rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        padding: 0 18px;
        border-radius: 10px 10px 0 0;
        font-size: 0.98rem;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# RENDERIZAÇÃO DOS CHIPS DE POS TAGGING
# ============================================================================

def renderizar_tokens_html(tokens: list[TokenAnalisado], destacar_palavra: str | None = None) -> str:
    """Renderiza os cartões visuais de cada token com sua classe gramatical e lema."""
    blocos = ['<div class="token-stage">']
    for t in tokens:
        info = POS_INFO[t.classe]
        texto_esc = html.escape(t.texto)
        lema_esc = html.escape(t.lema)
        destaque_extra = ""
        if destacar_palavra and t.normalizado == destacar_palavra.lower():
            destaque_extra = "box-shadow: 0 0 0 4px #FACC15, 0 8px 18px rgba(0,0,0,0.14); transform: scale(1.05);"

        amb_html = '<span class="ambig-badge">⚡ Ambígua</span>' if t.eh_ambigua else ""
        lema_html = (
            f'<span class="token-lemma">lema: <b>{lema_esc}</b></span>'
            if t.classe in ("SUB", "VERB", "ADJ")
            else f'<span class="token-lemma">{t.upos_spacy}</span>'
        )

        bloco = (
            f'<div class="token-chip" style="background:{info["cor_fundo"]}; '
            f'border-color:{info["cor_borda"]}; color:{info["cor_texto"]}; {destaque_extra}">'
            f'<div class="token-word">{texto_esc}</div>'
            f'<div class="token-pos">{info["icone"]} {info["nome_curto"]}</div>'
            f'{lema_html}'
            f'{amb_html}'
            f'</div>'
        )
        blocos.append(bloco)
    blocos.append("</div>")
    return "".join(blocos)


# ============================================================================
# DADOS DE DESAMBIGUAÇÃO E DO DESAFIO INTERATIVO
# ============================================================================

CASOS_AMBIGUIDADE = {
    "🎮 JOGO — Ação de jogar (Verbo) vs. O game em si (Substantivo)": {
        "palavra": "jogo",
        "frase_1": "Toda sexta eu jogo bola na quadra e depois treino online.",
        "titulo_1": "Contexto 1: Predicado Verbal",
        "explicacao_1": "Precedido pelo pronome sujeito **«eu»**, **«jogo»** é classificado como **Verbo** e reduzido ao infinitivo **`jogar`**.",
        "frase_2": "Esse jogo de mundo aberto tem gráficos absurdos.",
        "titulo_2": "Contexto 2: Núcleo Nominal",
        "explicacao_2": "Precedido pelo determinante demonstrativo **«Esse»**, **«jogo»** é um **Substantivo** (mantendo o lema **`jogo`**).",
    },
    "😂 RIO — Dar risada (Verbo rir) vs. Curso d'água (Substantivo rio)": {
        "palavra": "rio",
        "frase_1": "Eu rio demais com esses vídeos curtos de stand-up.",
        "titulo_1": "Contexto 1: Conjugação do verbo «rir»",
        "explicacao_1": "Sem POS Tagging, um *stemmer* cortaria «rio» para `ri` sem saber se é água ou risada. Com a etiqueta **Verbo**, a lematização mapeia `rio → rir`!",
        "frase_2": "A travessia de caiaque pelo rio exige bastante preparo.",
        "titulo_2": "Contexto 2: Substantivo «rio»",
        "explicacao_2": "Logo após a contração **«pelo»** (por + o), o modelo identifica **Substantivo**, preservando o lema **`rio`**.",
    },
    "🎤 CANTO — Cantar música (Verbo) vs. Espaço físico (Substantivo)": {
        "palavra": "canto",
        "frase_1": "Eu canto na banda da escola desde o ano passado.",
        "titulo_1": "Contexto 1: Verbo «cantar»",
        "explicacao_1": "Após **«Eu»**, atua como verbo na 1ª pessoa do singular → lema **`cantar`**.",
        "frase_2": "Coloquei a mesa do computador no canto do quarto.",
        "titulo_2": "Contexto 2: Substantivo «canto»",
        "explicacao_2": "Após **«no»** (em + o), refere-se a um ponto do espaço físico → lema **`canto`**.",
    },
    "💳 BANCO — Patrocinar/Pagar (Verbo bancar) vs. Instituição/Assento (Substantivo)": {
        "palavra": "banco",
        "frase_1": "Se todo mundo passar na prova, eu banco o açaí da galera!",
        "titulo_1": "Contexto 1: Verbo «bancar»",
        "explicacao_1": "Depois do sujeito **«eu»** e seguido do objeto «o açaí», funciona como **Verbo** → lema **`bancar`**.",
        "frase_2": "Abri minha primeira conta pelo aplicativo do banco digital.",
        "titulo_2": "Contexto 2: Substantivo «banco»",
        "explicacao_2": "Introduzido por **«do»** e qualificado por «digital», é um **Substantivo** → lema **`banco`**.",
    },
    "🥭 MANGA — Caçoar/Zombar (Verbo mangar) vs. Fruta ou Camisa (Substantivo)": {
        "palavra": "manga",
        "frase_1": "Ele nunca manga dos amigos quando alguém erra a questão.",
        "titulo_1": "Contexto 1: Verbo «mangar»",
        "explicacao_1": "Após o sujeito e o advérbio de negação (**«Ele nunca»**), é classificado como **Verbo** → lema **`mangar`**.",
        "frase_2": "Comprei um suco de manga gelado depois da aula.",
        "titulo_2": "Contexto 2: Substantivo «manga»",
        "explicacao_2": "Após a preposição **«de»** e seguido do adjetivo «gelado», é **Substantivo** → lema **`manga`**.",
    },
    "🏊 NADA — Locomover-se na água (Verbo nadar) vs. Nenhuma coisa (Pronome)": {
        "palavra": "nada",
        "frase_1": "Aquele atleta nada cem metros em menos de um minuto.",
        "titulo_1": "Contexto 1: Verbo «nadar»",
        "explicacao_1": "Posicionado como ação do sujeito «Aquele atleta», é3ª pessoa do verbo **`nadar`**.",
        "frase_2": "A gente não entendeu nada daquela questão difícil.",
        "titulo_2": "Contexto 2: Pronome Indefinido «nada»",
        "explicacao_2": "Em construção negativa após o verbo («não entendeu nada»), é classificado como **Pronome** (e filtrado no índice).",
    },
}

QUESTOES_DESAFIO = [
    {
        "categoria": "⚡ Desambiguação Clássica",
        "frase": "Eu rio toda vez que vejo esse corte, mas nunca nadei naquele rio.",
        "foco_exibicao": "1º «rio» (em «Eu rio»)",
        "correta": "VERB",
        "dica": "Observe quem vem imediatamente antes do primeiro «rio» e qual seria o infinitivo dessa palavra.",
        "explicacao": "No primeiro trecho (**«Eu rio»**), a palavra vem após o pronome sujeito «Eu» e é conjugação do **Verbo `rir`**. Já no final (**«naquele rio»**), após o determinante «naquele», é **Substantivo (`rio`)**!",
    },
    {
        "categoria": "🎮 Neologismos & Gírias na Web",
        "frase": "O time inteiro tankou a partida até o último segundo.",
        "foco_exibicao": "«tankou»",
        "correta": "VERB",
        "dica": "Mesmo que «tankar» venha dos games, olhe a terminação «-ou» e a posição entre «O time inteiro» e «a partida»!",
        "explicacao": "Exato! Modelos de POS Tagging conseguem classificar gírias e neologismos porque analisam a **morfologia** (sufixo verbal `-ou` do pretérito perfeito) e a **posição sintática** após o sujeito «O time inteiro» → **Verbo (`tankar`)**!",
    },
    {
        "categoria": "🔍 Filtragem em Buscadores",
        "frase": "Os estudantes pesquisaram sobre inteligência artificial na biblioteca.",
        "foco_exibicao": "«sobre»",
        "correta": "CON",
        "dica": "Essa palavra tem conteúdo próprio ou serve apenas para ligar o verbo «pesquisaram» ao tema «inteligência artificial»?",
        "explicacao": "Correto! **«sobre»** é uma preposição (**Conector / Palavra Funcional**). Ela ajuda o etiquetador a prever que virá um substantivo depois, mas é descartada como *Stop Word* na hora de indexar no motor de busca.",
    },
    {
        "categoria": "🎭 Palavra Polissêmica",
        "frase": "Deixei o violão encostado no canto escuro do estúdio.",
        "foco_exibicao": "«canto»",
        "correta": "SUB",
        "dica": "Repare na contração «no» (em + o) antes da palavra e no adjetivo «escuro» logo depois.",
        "explicacao": "Mandou bem! Embora «canto» possa ser 1ª pessoa do verbo *cantar*, estar entre o artigo embutido em **«no»** e o adjetivo **«escuro»** crava que é um **Substantivo**.",
    },
    {
        "categoria": "✨ Modificadores & Sentimento",
        "frase": "O novo algoritmo deixou a busca absurdamente rápida.",
        "foco_exibicao": "«absurdamente»",
        "correta": "ADV",
        "dica": "Olhe o sufixo «-mente» e veja que ela está intensificando o adjetivo «rápida».",
        "explicacao": "Perfeito! Palavras terminadas em `-mente` que intensificam um adjetivo ou verbo são **Advérbios (`ADV`)**.",
    },
    {
        "categoria": "💳 Homógrafo no Cotidiano",
        "frase": "Relaxa, hoje eu banco o ingresso do cinema pra você!",
        "foco_exibicao": "«banco»",
        "correta": "VERB",
        "dica": "Aqui «banco» é uma agência bancária/assento ou significa «eu pago / eu patrociínio»?",
        "explicacao": "Na mosca! Precedido por **«eu»** e seguido pelo objeto direto «o ingresso», **«banco»** é forma conjugada do **Verbo `bancar`**!",
    },
]


# ============================================================================
# SIDEBAR: LEGENDA RÁPIDA E CONTEXTO DA FEIRA
# ============================================================================

with st.sidebar:
    st.markdown("### ⚡ Guia de Classes (POS Tags)")
    st.caption(
        "Veja como o classificador morfossintático separa as palavras que carregam o **tema da busca** daquelas que apenas **estruturam a frase**:"
    )

    for codigo in ["SUB", "VERB", "ADJ", "ADV", "PRON", "CON"]:
        info = POS_INFO[codigo]
        st.markdown(
            f"""
            <div style="background:{info['cor_fundo']}; border-left: 5px solid {info['cor_borda']};
                        padding: 8px 11px; border-radius: 9px; margin-bottom: 7px; color:{info['cor_texto']};">
                <div style="font-weight:800; font-size:0.92rem;">
                    {info['icone']} {info['nome_exibicao']} <span style="opacity:0.75; font-size:0.76rem;">({info['codigo_tecnico']})</span>
                </div>
                <div style="font-size:0.78rem; margin-top:2px;">{info['papel']}</div>
                <div style="font-size:0.73rem; margin-top:3px; font-weight:700; opacity:0.9;">🔍 Busca: {info['peso_ri']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.caption(
        "🎓 **Feira de Extensão — ICMC/USP**\n\n"
        "**Disciplina:** SCC0282 — Recuperação de Informação\n\n"
        "**Integrantes:**\n"
        "- Ana Paula de Abreu Batista\n"
        "- Italo Carlos Martins Bresciani"
    )


# ============================================================================
# BANNER PRINCIPAL
# ============================================================================

st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-badge">PLN & Recuperação de Informação • Feira de Extensão USP</div>
        <h1>⚡ Como o Google e as IAs Entendem o Português?</h1>
        <p>Descubra na prática como o <b>Part-of-Speech Tagging (Etiquetagem Morfossintática)</b> resolve ambiguidades, entende gírias pelo contexto e impede que buscadores confundam palavras idênticas.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# ABAS PRINCIPAIS
# ============================================================================

aba_raiox, aba_ambiguidade, aba_busca, aba_desafio, aba_arquitetura = st.tabs(
    [
        "🔍 1. Raio-X da Frase",
        "🎭 2. Ambiguidade & Palavras Gêmeas",
        "🚀 3. Simulador de Motor de Busca",
        "⚡ 4. Desafio: Você vs. IA",
        "⚙️ 5. Por Trás do Código (spaCy + NLTK)",
    ]
)


# ----------------------------------------------------------------------------
# ABA 1: RAIO-X SINTÁTICO AO VIVO
# ----------------------------------------------------------------------------
with aba_raiox:
    st.markdown("### 🔍 Analisador Morfossintático em Tempo Real")
    st.write(
        "Quando você digita uma pesquisa ou manda uma mensagem para uma IA, o computador não lê o texto como um bloco único: "
        "ele **identifica o papel gramatical de cada palavra pelo contexto** para saber o que é ação, o que é assunto principal e o que pode ser descartado."
    )

    exemplos_frases = [
        "Eu rio demais com esses vídeos, mesmo morando perto do rio!",
        "Toda sexta eu jogo bola, mas esse jogo novo tá absurdo.",
        "O time inteiro tankou a partida até o último segundo!",
        "Eu canto na banda e deixei meu violão no canto do quarto.",
        "Hoje eu banco o lanche se a gente achar um banco vazio na praça.",
    ]

    if "frase_ativa" not in st.session_state:
        st.session_state.frase_ativa = exemplos_frases[0]

    st.markdown("**Teste com um exemplo rápido (note as palavras repetidas com sentidos diferentes e as gírias):**")
    cols_btn = st.columns(len(exemplos_frases))
    rotulos_curtos = [
        "😂 «Eu rio» vs «do rio»",
        "🎮 «eu jogo» vs «esse jogo»",
        "⚡ Gíria: «tankou a partida»",
        "🎤 «Eu canto» vs «no canto»",
        "💳 «eu banco» vs «um banco»",
    ]
    for i, f_ex in enumerate(exemplos_frases):
        if cols_btn[i].button(rotulos_curtos[i], width="stretch", key=f"ex_btn_{i}"):
            st.session_state.frase_ativa = f_ex

    frase_input = st.text_input(
        "✍️ Digite qualquer frase, pesquisa ou até gírias para passar no Raio-X:",
        value=st.session_state.frase_ativa,
        key="input_raiox",
    )

    if frase_input.strip():
        tokens = analisar_frase(frase_input)

        st.markdown("#### 1️⃣ Etiquetagem Morfossintática e Lematização Contextual")
        st.markdown(renderizar_tokens_html(tokens), unsafe_allow_html=True)

        ambiguas = [t for t in tokens if t.eh_ambigua]
        if ambiguas:
            lista_amb = ", ".join(f"**«{t.texto}»** ({POS_INFO[t.classe]['nome_curto']} → `{t.lema}`)" for t in ambiguas)
            st.info(
                f"⚡ **Desambiguação Ativa:** O analisador detectou palavra(s) homógrafa(s) na frase e definiu seu sentido pela estrutura sintática: {lista_amb}."
            )

        col_esq, col_dir = st.columns([1.4, 1.0], gap="large")

        with col_esq:
            st.markdown("#### 2️⃣ Como o modelo decidiu cada etiqueta?")
            for t in tokens:
                if t.classe == "PUNCT":
                    continue
                info = POS_INFO[t.classe]
                st.markdown(
                    f"""
                    <div class="info-card" style="border-left-color:{info['cor_borda']};">
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                            <span style="font-size:1.08rem; font-weight:800; color:{info['cor_texto']};">
                                {info['icone']} «{html.escape(t.texto)}» → {info['nome_exibicao']}
                            </span>
                            <span style="font-size:0.82rem; background:{info['cor_fundo']}; color:{info['cor_texto']};
                                         padding:2px 10px; border-radius:99px; border:1px solid {info['cor_borda']}; font-family:monospace; font-weight:700;">
                                lema: {html.escape(t.lema)} | UPOS: {t.upos_spacy}
                            </span>
                        </div>
                        <div style="margin-top:5px; font-size:0.92rem; color:#334155;">
                            {t.pista_contexto}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with col_dir:
            st.markdown("#### 3️⃣ Visão do Motor de Busca (Indexação)")
            sem_punct = [t for t in tokens if t.classe != "PUNCT"]
            indexados = [t for t in sem_punct if not t.eh_stopword]
            descartados = [t for t in sem_punct if t.eh_stopword]

            m1, m2 = st.columns(2)
            m1.metric("📌 Termos Indexados", len(indexados), help="Substantivos, Verbos e Adjetivos que vão para o índice invertido.")
            m2.metric("🧹 Stop Words Filtradas", len(descartados), help="Conectores e pronomes descartados após ajudarem na análise sintática.")

            st.markdown("**O que entra no Índice Invertido do Buscador:**")
            if indexados:
                chips_index = " ".join(
                    f"`({t.lema}, {POS_INFO[t.classe]['nome_curto']})`" for t in indexados
                )
                st.success(f"**Pares (Lema, Classe) armazenados:**\n\n{chips_index}")
            if descartados:
                txt_desc = ", ".join(f"«{t.texto}»" for t in descartados)
                st.caption(f"🗑️ **Removidas na filtragem seletiva:** {txt_desc}")

            st.markdown("---")
            st.markdown("**Distribuição gramatical da sentença:**")
            contagem: dict[str, int] = {}
            for t in sem_punct:
                contagem[t.classe] = contagem.get(t.classe, 0) + 1
            tot = max(1, len(sem_punct))
            for c_cod, qtd in sorted(contagem.items(), key=lambda x: x[1], reverse=True):
                inf = POS_INFO[c_cod]
                pct = int(round((qtd / tot) * 100))
                st.markdown(
                    f"""
                    <div style="margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; font-size:0.86rem; font-weight:700;">
                            <span>{inf['icone']} {inf['nome_exibicao']}</span>
                            <span>{qtd} ({pct}%)</span>
                        </div>
                        <div style="background:#E2E8F0; border-radius:99px; height:10px; overflow:hidden; margin-top:3px;">
                            <div style="background:{inf['cor_borda']}; width:{pct}%; height:100%;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ----------------------------------------------------------------------------
# ABA 2: AMBIGUIDADE & PALAVRAS GÊMEAS (LEMATIZAÇÃO CONTEXTUAL)
# ----------------------------------------------------------------------------
with aba_ambiguidade:
    st.markdown("### 🎭 O Problema das Palavras Gêmeas (Polissemia e Homografia)")
    st.write(
        "Em português, dezenas de verbos conjugados na 1ª pessoa (`eu rio`, `eu jogo`, `eu canto`, `eu banco`) "
        "ou na 3ª pessoa (`ele manga`, `ela casa`, `ele nada`) são escritos **exatamente igual** a substantivos ou pronomes. "
        "Veja por que um buscador precisa saber a classe gramatical antes de reduzir a palavra à raiz:"
    )

    escolha_caso = st.selectbox(
        "Escolha um par ambíguo para comparar:",
        list(CASOS_AMBIGUIDADE.keys()),
    )

    dados = CASOS_AMBIGUIDADE[escolha_caso]
    palavra_foco = dados["palavra"]

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown(f"#### {dados['titulo_1']}")
        t1 = analisar_frase(dados["frase_1"])
        st.markdown(renderizar_tokens_html(t1, destacar_palavra=palavra_foco), unsafe_allow_html=True)
        alvo1 = next((x for x in t1 if x.normalizado == palavra_foco), t1[0])
        inf1 = POS_INFO[alvo1.classe]
        st.markdown(
            f"""
            <div class="info-card" style="border-left-color:{inf1['cor_borda']};">
                <div style="font-weight:800; color:{inf1['cor_texto']}; font-size:1.05rem;">
                    Etiqueta: {inf1['icone']} {inf1['nome_exibicao']} ({alvo1.upos_spacy})
                </div>
                <div style="margin-top:4px; font-family:monospace; font-size:0.9rem;">
                    ✅ Lema com POS: <b>{alvo1.lema}</b> &nbsp;|&nbsp; ⚠️ Radical cego (Stemmer): <b>{alvo1.stem_nltk}</b>
                </div>
                <div style="margin-top:6px; font-size:0.92rem;">{dados['explicacao_1']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(f"#### {dados['titulo_2']}")
        t2 = analisar_frase(dados["frase_2"])
        st.markdown(renderizar_tokens_html(t2, destacar_palavra=palavra_foco), unsafe_allow_html=True)
        alvo2 = next((x for x in t2 if x.normalizado == palavra_foco), t2[0])
        inf2 = POS_INFO[alvo2.classe]
        st.markdown(
            f"""
            <div class="info-card" style="border-left-color:{inf2['cor_borda']};">
                <div style="font-weight:800; color:{inf2['cor_texto']}; font-size:1.05rem;">
                    Etiqueta: {inf2['icone']} {inf2['nome_exibicao']} ({alvo2.upos_spacy})
                </div>
                <div style="margin-top:4px; font-family:monospace; font-size:0.9rem;">
                    ✅ Lema com POS: <b>{alvo2.lema}</b> &nbsp;|&nbsp; ⚠️ Radical cego (Stemmer): <b>{alvo2.stem_nltk}</b>
                </div>
                <div style="margin-top:6px; font-size:0.92rem;">{dados['explicacao_2']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(f"#### 🧪 Teste de Fogo: Use **«{palavra_foco}»** duas vezes na mesma frase!")
    frase_dupla = st.text_input(
        f"Escreva uma frase em que «{palavra_foco}» apareça como Verbo e como Substantivo:",
        value=f"Sempre que eu {palavra_foco}, todo mundo comenta sobre esse {palavra_foco}!",
        key="input_teste_duplo",
    )
    if frase_dupla.strip():
        tokens_duplos = analisar_frase(frase_dupla)
        st.markdown(renderizar_tokens_html(tokens_duplos, destacar_palavra=palavra_foco), unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# ABA 3: SIMULADOR DE MOTOR DE BUSCA (RECUPERAÇÃO DE INFORMAÇÃO)
# ----------------------------------------------------------------------------
with aba_busca:
    st.markdown("### 🚀 Simulador de Busca: Literal/Radical vs. Busca com POS Tagging")
    st.write(
        "Compare o que acontece quando pesquisamos em uma base de notícias e posts usando:\n"
        "- **⚠️ Busca Sem POS Tagging (Literal + Stemmer Cego):** Corta sufixos sem olhar a classe gramatical — mistura *rio* (água) com *rio* (verbo *rir*) e *canto* (quarto) com *canto* (música).\n"
        "- **✅ Busca Inteligente (POS Tagging + Lematização Contextual):** Filtra *stop words* funcionais e casa o par `(lema, classe_gramatical)`, encontrando também outras conjugações do mesmo verbo (`rio` → `rir` encontra `riram`, `riu`)!"
    )

    consultas_demo = [
        "Eu rio muito com vídeos",
        "Travessia pelo rio gelado",
        "Eu canto na escola",
        "Mesa no canto da parede",
        "Eu jogo com meu time",
        "Lançamento do novo jogo",
        "Eu banco o lanche da galera",
        "Abrir conta no banco digital",
    ]

    if "query_ativa" not in st.session_state:
        st.session_state.query_ativa = consultas_demo[0]

    st.markdown("**Clique em uma consulta para comparar os dois motores de busca:**")
    cols_q = st.columns(4)
    for idx_q, q_str in enumerate(consultas_demo):
        if cols_q[idx_q % 4].button(f"🔍 {q_str}", width="stretch", key=f"q_btn_{idx_q}"):
            st.session_state.query_ativa = q_str

    query_user = st.text_input(
        "Ou digite sua própria consulta de busca:",
        value=st.session_state.query_ativa,
        key="input_query_ri",
    )

    if query_user.strip():
        res = buscar_documentos(query_user)
        semanticos: list[TokenAnalisado] = res["termos_semanticos"]  # type: ignore
        removidas: list[TokenAnalisado] = res["stopwords_removidas"]  # type: ignore

        c_prep1, c_prep2 = st.columns(2, gap="large")
        with c_prep1:
            if removidas:
                rem_str = ", ".join(f"«{t.texto}» ({POS_INFO[t.classe]['nome_curto']})" for t in removidas)
                st.warning(f"🧹 **1. Filtragem Seletiva de Stop Words:** descartou {rem_str}")
            else:
                st.info("🧹 **1. Filtragem Seletiva:** nenhuma stop word funcional na consulta.")
        with c_prep2:
            if semanticos:
                sem_str = " • ".join(
                    f"**{t.texto}** → `({t.lema}, {POS_INFO[t.classe]['nome_curto']})`" for t in semanticos
                )
                st.success(f"🎯 **2. Consulta Estruturada (Lema + POS):** {sem_str}")

        col_sem_pos, col_com_pos = st.columns(2, gap="large")

        with col_sem_pos:
            st.markdown("#### ⚠️ Busca Sem POS Tagging (Literal / Stemmer)")
            st.caption("Ignora a classe gramatical — traz falsos positivos por homografia ou perde verbos irregulares:")
            lista_sem = res["resultados_sem_pos"]  # type: ignore
            if not lista_sem:
                st.error("Nenhum documento encontrado.")
            for item in lista_sem:
                d = item["documento"]
                m_str = ", ".join(item["matches"])
                st.markdown(
                    f"""
                    <div class="info-card" style="border-left-color:#F59E0B; background:#FFFBEB;">
                        <div style="font-weight:800; font-size:1.05rem; color:#92400E;">
                            {d.icone} {d.titulo} <span style="font-size:0.78rem; opacity:0.8;">({d.categoria})</span>
                        </div>
                        <div style="margin:5px 0; font-size:0.92rem; color:#334155;">{d.texto}</div>
                        <div style="font-size:0.8rem; color:#B45309;">⚠️ Casamento superficial: {m_str}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with col_com_pos:
            st.markdown("#### ✅ Busca Com POS Tagging + Lematização")
            st.caption("Desambigua a função sintática na consulta e nos documentos, recuperando apenas o sentido correto:")
            lista_com = res["resultados_com_pos"]  # type: ignore
            if not lista_com:
                st.warning("Nenhum documento com esse par (lema, classe) na coleção.")
            for item in lista_com:
                d = item["documento"]
                m_str = ", ".join(item["matches"])
                st.markdown(
                    f"""
                    <div class="info-card" style="border-left-color:#10B981; background:#ECFDF5;">
                        <div style="font-weight:800; font-size:1.05rem; color:#065F46;">
                            {d.icone} {d.titulo} <span style="font-size:0.78rem; opacity:0.8;">({d.categoria})</span>
                        </div>
                        <div style="margin:5px 0; font-size:0.92rem; color:#1E293B;">{d.texto}</div>
                        <div style="font-size:0.8rem; color:#047857; font-weight:700;">✅ Casamento Semântico: {m_str}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ----------------------------------------------------------------------------
# ABA 4: DESAFIO VOCÊ VS. IA (QUIZ DE CONTEXTO)
# ----------------------------------------------------------------------------
with aba_desafio:
    st.markdown("### ⚡ Desafio Rápido: Você Desambigua Tão Bem Quanto o Modelo?")
    st.write("Analise o contexto sintático das frases abaixo (incluindo pegadinhas de homografia e gírias da internet) e escolha a etiqueta correta!")

    if "q_idx" not in st.session_state:
        st.session_state.q_idx = 0
    if "q_score" not in st.session_state:
        st.session_state.q_score = 0
    if "q_done" not in st.session_state:
        st.session_state.q_done = False
    if "q_hit" not in st.session_state:
        st.session_state.q_hit = False

    p1, p2, p3 = st.columns(3)
    p1.metric("🏆 Pontuação", f"{st.session_state.q_score} pts")
    p2.metric("📍 Rodada", f"{st.session_state.q_idx + 1} / {len(QUESTOES_DESAFIO)}")
    if p3.button("🔄 Reiniciar Desafio", width="stretch"):
        st.session_state.q_idx = 0
        st.session_state.q_score = 0
        st.session_state.q_done = False
        st.rerun()

    questao = QUESTOES_DESAFIO[st.session_state.q_idx]

    st.markdown(
        f"""
        <div style="background:#0F172A; color:#F8FAFC; border-radius:16px; padding:1.5rem; margin:1rem 0;">
            <div style="color:#818CF8; font-weight:800; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.05em;">
                {questao['categoria']}
            </div>
            <div style="font-size:1.45rem; font-weight:700; margin:10px 0; color:#FFFFFF;">
                “{questao['frase']}”
            </div>
            <div style="font-size:1.05rem; color:#CBD5E1;">
                Qual é a classe morfossintática de <b style="color:#FACC15;">{questao['foco_exibicao']}</b> nessa frase?
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("💡 Ver dica de análise sintática"):
        st.write(questao["dica"])

    alternativas = [
        ("SUB", "📘 Substantivo (Núcleo nominal / Entidade)"),
        ("VERB", "⚡ Verbo (Ação / Processo / Predicado)"),
        ("ADJ", "✨ Adjetivo (Qualificador nominal)"),
        ("ADV", "🎯 Advérbio (Modificador de intensidade/modo/tempo)"),
        ("CON", "🔗 Conector / Preposição (Stop Word funcional)"),
    ]

    cols_alt = st.columns(3)
    for i, (cod_a, rot_a) in enumerate(alternativas):
        if cols_alt[i % 3].button(
            rot_a,
            key=f"alt_{st.session_state.q_idx}_{cod_a}",
            width="stretch",
            disabled=st.session_state.q_done,
        ):
            st.session_state.q_done = True
            if cod_a == questao["correta"]:
                st.session_state.q_hit = True
                st.session_state.q_score += 10
                st.balloons()
            else:
                st.session_state.q_hit = False
            st.rerun()

    if st.session_state.q_done:
        if st.session_state.q_hit:
            st.success(f"✅ **Na mosca! (+10 pts)** — {questao['explicacao']}")
        else:
            certa_info = POS_INFO[questao["correta"]]
            st.error(
                f"❌ **Quase!** A etiqueta correta é **{certa_info['icone']} {certa_info['nome_exibicao']}**.\n\n"
                f"{questao['explicacao']}"
            )

        st.markdown("**Raio-X completo da frase gerado pelo modelo:**")
        st.markdown(renderizar_tokens_html(analisar_frase(questao["frase"])), unsafe_allow_html=True)

        if st.session_state.q_idx + 1 < len(QUESTOES_DESAFIO):
            if st.button("➡️ Próxima Questão", type="primary", width="stretch"):
                st.session_state.q_idx += 1
                st.session_state.q_done = False
                st.rerun()
        else:
            st.success(
                f"🏁 **Desafio Concluído!** Você marcou **{st.session_state.q_score} de {len(QUESTOES_DESAFIO) * 10} pontos**!"
            )


# ----------------------------------------------------------------------------
# ABA 5: ARQUITETURA & CÓDIGO (SPACY + NLTK)
# ----------------------------------------------------------------------------
with aba_arquitetura:
    st.markdown("### ⚙️ Por Trás do Código: Pipeline de PLN e Recuperação de Informação")
    st.write(
        "Esta seção detalha a implementação técnica do projeto para a disciplina **SCC0282 — Recuperação de Informação (ICMC/USP)**."
    )

    c_t1, c_t2, c_t3 = st.columns(3)
    with c_t1:
        st.markdown(
            """
            #### 1. POS Tagging (`spaCy pt_core_news_sm`)
            - Pipeline neural treinado em corpora do português (*Bosque / Universal Dependencies*).
            - Extrai *Universal POS Tags* (`NOUN`, `VERB`, `ADJ`, `ADP`, `DET`, `PRON`, `ADV`), feições morfológicas (`Gender`, `Number`, `Tense`, `VerbForm`) e árvore de dependências (`dep_`).
            - Camada adicional de desambiguação contextual para homógrafos verbo-nominais e gírias/neologismos.
            """
        )
    with c_t2:
        st.markdown(
            """
            #### 2. Lematização Contextual vs. Stemming (`NLTK`)
            - O *stemmer* **RSLP do NLTK** remove sufixos de forma estática, colapsando o substantivo **«rio»** e a forma verbal **«rio»** (*rir*) no mesmo radical `ri`.
            - Com a classe gramatical inferida pelo POS Tagger antes da normalização:
              - `("rio", VERB) → "rir"`
              - `("rio", SUB) → "rio"`
            """
        )
    with c_t3:
        st.markdown(
            """
            #### 3. Indexação e Busca (SCC0282)
            - **Filtragem Seletiva:** Descarte guiado por classes funcionais (`DET`, `ADP`, `CCONJ`, `SCONJ`, `PRON`) em conjunto com a lista de *stopwords* do NLTK.
            - **Desambiguação no Índice Invertido:** Representação dos termos como tuplas `(lema, classe_pos)`, evitando colisões de polissemia entre documentos e consultas (*queries*).
            """
        )

    st.markdown("---")
    st.markdown("#### 🔬 Tabela de Inspeção Técnica (spaCy + NLTK)")
    frase_tec = st.text_input(
        "Sentença para inspeção de atributos internos:",
        value="Eu rio demais com esses vídeos, mesmo morando perto do rio!",
        key="input_tabela_tec",
    )
    if frase_tec.strip():
        tokens_tec = analisar_frase(frase_tec)
        linhas = []
        for idx_t, t in enumerate(tokens_tec, start=1):
            info = POS_INFO[t.classe]
            linhas.append(
                {
                    "#": idx_t,
                    "Token": t.texto,
                    "Classe": f"{info['icone']} {info['nome_exibicao']}",
                    "UPOS (spaCy)": t.upos_spacy,
                    "Dependência (dep_)": t.dep_spacy,
                    "Morfologia (morph)": t.morfologia_spacy,
                    "Lema Contextual": t.lema,
                    "Stem RSLP (NLTK)": t.stem_nltk,
                    "Indexado na Busca?": "Não (Stop Word 🧹)" if t.eh_stopword else f"Sim → ({t.lema}, {info['nome_curto']})",
                }
            )
        st.dataframe(linhas, width="stretch", hide_index=True)
