"""
Motor de Processamento de Linguagem Natural (POS Tagging, Lematização Contextual
e Recuperação de Informação) desenvolvido para a Feira de Extensão — SCC0282.

Público-alvo: Estudantes de Ensino Médio (16–18 anos) e visitantes da feira.
Utiliza:
- spaCy (`pt_core_news_sm`) para tokenização, POS Tagging (Universal POS Tags),
  feições morfológicas (`morph`), análise sintática (`dep_`) e lematização (`lemma_`).
- NLTK (`nltk.corpus.stopwords` e `nltk.stem.RSLPStemmer`) para comparação entre
  Stemming tradicional e Lematização Contextualizada guiada por classe gramatical.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass, field
from typing import Dict, List

import nltk
import spacy
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer


# ============================================================================
# 1. INICIALIZAÇÃO DO SPACY E DO NLTK (COM CACHE)
# ============================================================================

class _FallbackRSLPStemmer:
    """Fallback caso os arquivos de dados do RSLP ainda não tenham sido baixados."""

    def stem(self, word: str) -> str:
        for suf in (
            "mente", "ções", "ção", "inhos", "inhas", "inho", "inha",
            "aram", "eram", "iram", "ando", "endo", "indo", "oso", "osa",
            "ar", "er", "ir", "ou", "iu", "eu", "s", "o", "a", "e",
        ):
            if len(word) - len(suf) >= 2 and word.endswith(suf):
                return word[: -len(suf)]
        return word


@functools.lru_cache(maxsize=1)
def carregar_recursos_nlp():
    """Carrega o modelo em português do spaCy (`pt_core_news_sm`) e os recursos do NLTK."""
    nlp = spacy.load("pt_core_news_sm")

    try:
        nltk.data.find("stemmers/rslp")
        stemmer = RSLPStemmer()
    except LookupError:
        stemmer = _FallbackRSLPStemmer()

    try:
        nltk.data.find("corpora/stopwords")
        stop_pt = set(stopwords.words("portuguese"))
    except LookupError:
        stop_pt = set(nlp.Defaults.stop_words)

    return nlp, stemmer, stop_pt


# ============================================================================
# 2. CATEGORIAS GRAMATICAIS (CLARAS E DIRETAS PARA PÚBLICO DE 16–18 ANOS)
# ============================================================================

POS_INFO: Dict[str, Dict[str, str]] = {
    "SUB": {
        "codigo_tecnico": "NOUN / PROPN",
        "nome_exibicao": "Substantivo",
        "nome_curto": "Substantivo",
        "papel": "Entidades, objetos, lugares, conceitos e nomes próprios",
        "icone": "📘",
        "cor_fundo": "#EFF6FF",
        "cor_borda": "#2563EB",
        "cor_texto": "#1E3A8A",
        "explicacao": "Nomeia seres, objetos, lugares, ideias ou marcas. Nos buscadores, os substantivos costumam ser os termos principais do índice.",
        "exemplos": "jogo, rio, algoritmo, música, faculdade, celular",
        "peso_ri": "Alto (Indexado como termo-chave)",
    },
    "VERB": {
        "codigo_tecnico": "VERB / AUX",
        "nome_exibicao": "Verbo",
        "nome_curto": "Verbo",
        "papel": "Ações, processos, estados e fenômenos",
        "icone": "⚡",
        "cor_fundo": "#FEF2F2",
        "cor_borda": "#DC2626",
        "cor_texto": "#7F1D1D",
        "explicacao": "Indica ação, estado ou acontecimento. Como varia muito em tempo e pessoa, precisa ser reduzido ao infinitivo (lema) para a busca funcionar bem.",
        "exemplos": "jogar, rir, correr, programar, cantar, viajar",
        "peso_ri": "Alto (Lematizado para o infinitivo)",
    },
    "ADJ": {
        "codigo_tecnico": "ADJ",
        "nome_exibicao": "Adjetivo",
        "nome_curto": "Adjetivo",
        "papel": "Características, qualidades e estados atribuídos a um substantivo",
        "icone": "✨",
        "cor_fundo": "#F5F3FF",
        "cor_borda": "#7C3AED",
        "cor_texto": "#4C1D95",
        "explicacao": "Modifica um substantivo dando uma propriedade ou avaliação. Essencial para buscas específicas e análise de sentimento.",
        "exemplos": "rápido, incrível, difícil, gelado, absurdo, novo",
        "peso_ri": "Médio-Alto (Refina a busca)",
    },
    "ADV": {
        "codigo_tecnico": "ADV",
        "nome_exibicao": "Advérbio",
        "nome_curto": "Advérbio",
        "papel": "Modificador de verbo, adjetivo ou da frase inteira (tempo, modo, intensidade, negação)",
        "icone": "🎯",
        "cor_fundo": "#FFFBEB",
        "cor_borda": "#D97706",
        "cor_texto": "#78350F",
        "explicacao": "Indica circunstâncias (intensidade, tempo, lugar, negação). Palavras como «não» mudam totalmente o sentido de uma busca!",
        "exemplos": "muito, não, hoje, rápido, demais, perto",
        "peso_ri": "Médio (Contextualizador)",
    },
    "PRON": {
        "codigo_tecnico": "PRON",
        "nome_exibicao": "Pronome",
        "nome_curto": "Pronome",
        "papel": "Substitui ou acompanha os nomes indicando as pessoas do discurso",
        "icone": "👤",
        "cor_fundo": "#FDF2F8",
        "cor_borda": "#DB2777",
        "cor_texto": "#831843",
        "explicacao": "Retoma ou aponta quem realiza a ação («eu», «ele», «isso»). Ajuda a IA a descobrir que a próxima palavra é um verbo, mas geralmente é filtrado na indexação.",
        "exemplos": "eu, você, ele, nós, meu, esse, nada",
        "peso_ri": "Baixo (Usado no contexto, filtrado no índice)",
    },
    "CON": {
        "codigo_tecnico": "DET / ADP / CCONJ / SCONJ",
        "nome_exibicao": "Conector / Funcional",
        "nome_curto": "Conector",
        "papel": "Artigos, preposições e conjunções que estruturam a sintaxe",
        "icone": "🔗",
        "cor_fundo": "#F1F5F9",
        "cor_borda": "#64748B",
        "cor_texto": "#334155",
        "explicacao": "Palavras funcionais (artigos, preposições, conjunções). São cruciais para determinar a classe da palavra seguinte, mas são removidas como Stop Words no motor de busca.",
        "exemplos": "o, a, de, no, para, com, mas, quando, que",
        "peso_ri": "Stop Word (Removida após análise sintática)",
    },
    "NUM": {
        "codigo_tecnico": "NUM",
        "nome_exibicao": "Numeral",
        "nome_curto": "Numeral",
        "papel": "Quantidades, datas, ordens e medidas",
        "icone": "🔢",
        "cor_fundo": "#F0FDFA",
        "cor_borda": "#0D9488",
        "cor_texto": "#134E4A",
        "explicacao": "Quantifica elementos ou indica posição/ano.",
        "exemplos": "dois, 2026, primeiro, mil, 10",
        "peso_ri": "Médio (Filtros exatos)",
    },
    "PUNCT": {
        "codigo_tecnico": "PUNCT",
        "nome_exibicao": "Pontuação",
        "nome_curto": "Pontuação",
        "papel": "Delimitadores sintáticos e entonação",
        "icone": "▫️",
        "cor_fundo": "#F8FAFC",
        "cor_borda": "#94A3B8",
        "cor_texto": "#475569",
        "explicacao": "Delimita orações e expressa entonação; descartada no índice invertido.",
        "exemplos": ". , ! ? :",
        "peso_ri": "Ignorada no índice",
    },
}

MAPA_UPOS_PARA_CLASSE: Dict[str, str] = {
    "NOUN": "SUB",
    "PROPN": "SUB",
    "VERB": "VERB",
    "AUX": "VERB",
    "ADJ": "ADJ",
    "ADV": "ADV",
    "PRON": "PRON",
    "DET": "CON",
    "ADP": "CON",
    "CCONJ": "CON",
    "SCONJ": "CON",
    "PART": "CON",
    "INTJ": "CON",
    "NUM": "NUM",
    "PUNCT": "PUNCT",
    "SYM": "PUNCT",
    "X": "SUB",
}


# ============================================================================
# 3. PALAVRAS HOMÓGRAFAS / POLISSÊMICAS (DESAMBIGUAÇÃO VERBO vs. SUBSTANTIVO)
# ============================================================================

PALAVRAS_AMB: Dict[str, Dict[str, str]] = {
    "rio": {"SUB": "rio", "VERB": "rir"},
    "jogo": {"SUB": "jogo", "VERB": "jogar"},
    "canto": {"SUB": "canto", "VERB": "cantar"},
    "banco": {"SUB": "banco", "VERB": "bancar"},
    "manga": {"SUB": "manga", "VERB": "mangar"},
    "caminho": {"SUB": "caminho", "VERB": "caminhar"},
    "casa": {"SUB": "casa", "VERB": "casar"},
    "conta": {"SUB": "conta", "VERB": "contar"},
    "trabalho": {"SUB": "trabalho", "VERB": "trabalhar"},
    "sonho": {"SUB": "sonho", "VERB": "sonhar"},
    "pulo": {"SUB": "pulo", "VERB": "pular"},
    "olho": {"SUB": "olho", "VERB": "olhar"},
    "passo": {"SUB": "passo", "VERB": "passar"},
    "almoço": {"SUB": "almoço", "VERB": "almoçar"},
    "toque": {"SUB": "toque", "VERB": "tocar"},
    "corte": {"SUB": "corte", "VERB": "cortar"},
    "nada": {"VERB": "nadar", "PRON": "nada"},
}

DETERMINANTES_E_PREPOSICOES = {
    "o", "a", "os", "as", "um", "uma", "uns", "umas",
    "este", "esta", "esse", "essa", "aquele", "aquela",
    "meu", "minha", "seu", "sua", "nosso", "nossa",
    "do", "da", "dos", "das", "no", "na", "nos", "nas",
    "num", "numa", "pelo", "pela", "ao", "à", "pro", "pra",
    "de", "em", "sobre", "novo", "velho", "bom", "ótimo", "melhor",
}

MARCADORES_SUJEITO_E_ADV_VERBAIS = {
    "eu", "tu", "ele", "ela", "nós", "eles", "elas", "você", "vocês", "gente",
    "não", "nunca", "sempre", "já", "quando", "quem", "também", "só",
}


# ============================================================================
# 4. ESTRUTURA DE SAÍDA DE CADA TOKEN
# ============================================================================

@dataclass
class TokenAnalisado:
    texto: str
    normalizado: str
    classe: str
    upos_spacy: str
    dep_spacy: str
    morfologia_spacy: str
    lema: str
    stem_nltk: str
    pista_contexto: str
    eh_stopword: bool
    eh_ambigua: bool = False
    outras_classes_possiveis: List[str] = field(default_factory=list)


# ============================================================================
# 5. EXPLICAÇÕES DE CONTEXTO SINTÁTICO (ACESSÍVEIS PARA 16–18 ANOS)
# ============================================================================

def gerar_explicacao_contexto(
    indice: int,
    tokens_norm: List[str],
    tags: List[str],
    lema: str,
    eh_ambigua: bool,
) -> str:
    """Explica de forma clara e sem jargão pesado como o contexto definiu a etiqueta."""
    palavra = tokens_norm[indice]
    classe = tags[indice]
    ant_palavra = tokens_norm[indice - 1] if indice > 0 else None
    ant_classe = tags[indice - 1] if indice > 0 else None
    prox_palavra = tokens_norm[indice + 1] if indice + 1 < len(tokens_norm) else None
    prox_classe = tags[indice + 1] if indice + 1 < len(tags) else None

    if classe == "PUNCT":
        return "Delimitador de pontuação (ignorado na indexação)."

    if eh_ambigua:
        if classe == "SUB":
            if ant_palavra in DETERMINANTES_E_PREPOSICOES:
                return (
                    f"⚡ **Desambiguação por Contexto:** «{palavra}» poderia ser verbo ou substantivo, "
                    f"mas como vem precedida por «{ant_palavra}», atua como núcleo nominal (**Substantivo**, lema: `{lema}`)."
                )
            if prox_classe == "ADJ":
                return (
                    f"⚡ **Desambiguação por Contexto:** A presença do adjetivo «{prox_palavra}» logo em seguida "
                    f"confirma que «{palavra}» é um **Substantivo** (lema: `{lema}`)."
                )
            return (
                f"⚡ **Desambiguação por Contexto:** Pela posição sintática na oração, «{palavra}» foi "
                f"classificada como **Substantivo** (lema: `{lema}`), e não como forma verbal."
            )
        if classe == "VERB":
            if ant_classe in ("PRON", "SUB") or ant_palavra in MARCADORES_SUJEITO_E_ADV_VERBAIS:
                return (
                    f"⚡ **Desambiguação por Contexto:** Precedida pelo sujeito/modificador «{ant_palavra}», "
                    f"«{palavra}» exerce papel de predicado (**Verbo**, reduzido ao infinitivo `{lema}`)."
                )
            return (
                f"⚡ **Desambiguação por Contexto:** Pela estrutura da frase, «{palavra}» é uma forma conjugada "
                f"do **Verbo** `{lema}`."
            )
        if classe == "PRON" and palavra == "nada":
            return (
                f"⚡ **Desambiguação por Contexto:** Em contexto negativo («{ant_palavra or ''} nada»), "
                f"«nada» funciona como **Pronome Indefinido / Advérbio**, e não como o verbo *nadar*."
            )

    if classe == "CON":
        return (
            f"Palavra funcional («{palavra}») que conecta termos e dá pista sobre a classe da palavra seguinte. "
            f"É filtrada como *stop word* no buscador."
        )

    if classe == "PRON":
        return f"Pronome que indica pessoa ou referência no discurso; ajuda a prever verbos adjacentes."

    if classe == "SUB":
        if ant_palavra in DETERMINANTES_E_PREPOSICOES:
            return f"Introduzido por «{ant_palavra}», funciona como **Substantivo** (termo-chave indexado como `{lema}`)."
        return f"Identificado como **Substantivo** de alta carga semântica (indexado como `{lema}`)."

    if classe == "VERB":
        if palavra.endswith(("ou", "ava", "aram", "eram", "iram", "ando", "endo", "indo")):
            return (
                f"A terminação morfológica de «{palavra}» e a posição após «{ant_palavra or 'início'}» "
                f"indicam um **Verbo** (normalizado para o infinitivo `{lema}`)."
            )
        return f"Núcleo verbal da oração, reduzido ao infinitivo `{lema}` para unificar conjugações na busca."

    if classe == "ADJ":
        if ant_classe == "SUB":
            return f"Modifica diretamente o substantivo «{ant_palavra}», atribuindo-lhe uma característica (lema: `{lema}`)."
        return f"Qualificador nominal ou predicativo (lema: `{lema}`)."

    if classe == "ADV":
        return "Modificador circunstancial (intensidade, tempo, lugar ou negação)."

    if classe == "NUM":
        return "Expressão numérica ou quantificadora."

    return "Classificado pelo modelo estatístico/neural com base na vizinhança sintática."


# ============================================================================
# 6. PIPELINE PRINCIPAL COM SPACY + NLTK
# ============================================================================

def analisar_frase(frase: str) -> List[TokenAnalisado]:
    """
    Executa o pipeline completo de PLN usando spaCy (`pt_core_news_sm`) e NLTK (`RSLPStemmer`):
    1. Tokenização e etiquetagem morfossintática via spaCy
    2. Desambiguação contextual de homógrafos e gírias/neologismos verbais
    3. Lematização contextualizada vs. Stemming RSLP do NLTK
    """
    if not frase or not frase.strip():
        return []

    nlp, stemmer, stop_pt = carregar_recursos_nlp()
    doc = nlp(frase.strip())

    tokens_texto = [t.text for t in doc if not t.is_space]
    tokens_norm = [t.lower_ for t in doc if not t.is_space]
    tokens_spacy = [t for t in doc if not t.is_space]
    n = len(tokens_spacy)

    tags_finais: List[str] = []
    upos_lista: List[str] = []
    lemas_finais: List[str] = []

    for i, tok in enumerate(tokens_spacy):
        norm = tokens_norm[i]
        upos = tok.pos_
        classe = MAPA_UPOS_PARA_CLASSE.get(upos, "SUB")
        lema_spacy = tok.lemma_.lower() if tok.lemma_ else norm

        ant = tokens_norm[i - 1] if i > 0 else ""
        prox = tokens_norm[i + 1] if i + 1 < n else ""

        # Pronomes retos e oblíquos comuns
        if norm in ("eu", "tu", "ele", "ela", "nós", "eles", "elas", "você", "vocês", "me", "te", "se"):
            classe = "PRON"
            upos = "PRON"

        # Conectores subordinativos
        if norm in ("quando", "enquanto", "porque", "como", "se", "que", "embora"):
            classe = "CON"
            upos = "SCONJ"

        # Gírias/neologismos conjugados comuns entre jovens (ex: "tankou", "bugou", "flopou", "rushei", "cringe")
        if norm in ("tankou", "bugou", "flopou", "lagou", "dropou", "tiltou", "crushou"):
            classe = "VERB"
            upos = "VERB"
            lema_spacy = norm[:-2] + "ar"
        elif norm in ("hypado", "hypada", "bugado", "bugada", "tiltado", "absurdo", "absurda", "insano", "insana", "bizarro"):
            classe = "ADJ"
            upos = "ADJ"
            lema_spacy = norm[:-1] + "o" if norm.endswith("a") else norm
        elif norm == "tá":
            classe = "VERB"
            upos = "AUX"
            lema_spacy = "estar"
        elif norm == "pra":
            classe = "CON"
            upos = "ADP"
            lema_spacy = "para"

        # Particípios (-ado/-ada/-ido/-ida) funcionando como Adjetivo após Substantivo ou Verbo de ligação/Advérbio
        if (
            upos == "VERB"
            and "VerbForm=Part" in str(tok.morph)
            and i > 0
            and (
                tags_finais[-1] in ("SUB", "ADV")
                or tokens_norm[i - 1] in ("é", "está", "tá", "era", "estava", "ficou", "bem", "muito", "super", "meio")
            )
        ):
            classe = "ADJ"
            upos = "ADJ"
            lema_spacy = norm[:-1] + "o" if norm.endswith("a") else norm

        # Substantivos concretos que podem vir logo após um verbo desambiguado ("jogo bola", "banco o lanche")
        if norm in ("bola", "futebol", "partida", "violão", "música", "lanche", "açaí", "conta", "vídeo", "vídeos", "caiaque"):
            if norm != "conta" or ant in DETERMINANTES_E_PREPOSICOES:
                classe = "SUB"
                upos = "NOUN"
                lema_spacy = "vídeo" if norm == "vídeos" else norm

        # Adjetivos de cor/sabor após substantivo ("cachorro caramelo", "manga docinha")
        if norm in ("caramelo", "rosa", "laranja", "lilás", "docinha", "docinho") and i > 0 and tags_finais[-1] == "SUB":
            classe = "ADJ"
            upos = "ADJ"
            lema_spacy = "doce" if norm.startswith("docinh") else norm

        # Desambiguação de Palavras Homógrafas / Polissêmicas (Verbo vs. Substantivo)
        if norm in PALAVRAS_AMB:
            opcoes = PALAVRAS_AMB[norm]
            if norm == "nada":
                if ant in ("não", "nunca", "sem", "de", "") or prox in ("de", "disso", "aconteceu", "a", "ver"):
                    classe = "PRON"
                    upos = "PRON"
                    lema_spacy = "nada"
                elif i > 0 and tags_finais[-1] == "VERB":
                    classe = "PRON"
                    upos = "PRON"
                    lema_spacy = "nada"
                else:
                    classe = "VERB"
                    upos = "VERB"
                    lema_spacy = "nadar"
            elif ant in DETERMINANTES_E_PREPOSICOES:
                classe = "SUB"
                upos = "NOUN"
                lema_spacy = opcoes["SUB"]
            elif ant in MARCADORES_SUJEITO_E_ADV_VERBAIS or (i > 0 and tags_finais[-1] == "PRON"):
                classe = "VERB"
                upos = "VERB"
                lema_spacy = opcoes["VERB"]
            else:
                if classe == "VERB" and "VERB" in opcoes:
                    lema_spacy = opcoes["VERB"]
                elif classe == "SUB" and "SUB" in opcoes:
                    lema_spacy = opcoes["SUB"]

        # Garante infinitivo correto para formas irregulares de "rir"
        if classe == "VERB" and norm in ("rio", "ri", "riu", "riram", "rindo"):
            lema_spacy = "rir"

        tags_finais.append(classe)
        upos_lista.append(upos)
        lemas_finais.append(lema_spacy)

    resultado: List[TokenAnalisado] = []
    for i, tok in enumerate(tokens_spacy):
        orig = tokens_texto[i]
        norm = tokens_norm[i]
        classe = tags_finais[i]
        upos = upos_lista[i]
        lema = lemas_finais[i]

        eh_ambigua = norm in PALAVRAS_AMB
        outras_classes = list(PALAVRAS_AMB.get(norm, {}).keys())

        stem = stemmer.stem(norm) if classe != "PUNCT" else norm
        eh_stopword = classe in ("CON", "PRON", "PUNCT") or (norm in stop_pt and classe not in ("SUB", "VERB", "ADJ"))

        pista = gerar_explicacao_contexto(i, tokens_norm, tags_finais, lema, eh_ambigua)
        morf_str = str(tok.morph) if str(tok.morph) else "—"

        resultado.append(
            TokenAnalisado(
                texto=orig,
                normalizado=norm,
                classe=classe,
                upos_spacy=upos,
                dep_spacy=tok.dep_ or "—",
                morfologia_spacy=morf_str,
                lema=lema,
                stem_nltk=stem,
                pista_contexto=pista,
                eh_stopword=eh_stopword,
                eh_ambigua=eh_ambigua,
                outras_classes_possiveis=outras_classes,
            )
        )

    return resultado


# ============================================================================
# 7. SIMULADOR DE BUSCA (RECUPERAÇÃO DE INFORMAÇÃO — CONTEÚDO JOVEM / ATUAL)
# ============================================================================

@dataclass
class DocumentoBusca:
    id: int
    titulo: str
    icone: str
    categoria: str
    texto: str


COLECAO_DOCUMENTOS: List[DocumentoBusca] = [
    DocumentoBusca(
        id=1,
        titulo="Stand-up e Memes: Por que a gente ri tanto de vídeos curtos?",
        icone="😂",
        categoria="Cultura Pop & Redes",
        texto="Os criadores de conteúdo sabem exatamente como fazer o público rir em segundos. Eu rio demais com os cortes de stand-up e todo mundo riu na sala ontem.",
    ),
    DocumentoBusca(
        id=2,
        titulo="Expedição de Caiaque e Trilhas no Rio Paraná",
        icone="🛶",
        categoria="Viagem & Natureza",
        texto="A travessia pelo rio exige preparo físico. A água gelada do rio cria correntezas rápidas perto das pedras e atrai aventureiros no verão.",
    ),
    DocumentoBusca(
        id=3,
        titulo="Como treinar a voz e cantar melhor sem equipamentos caros",
        icone="🎤",
        categoria="Música & Áudio",
        texto="Eu canto na banda da escola desde o ano passado. Quando alguém canta afinado e controla a respiração, a gravação fica profissional.",
    ),
    DocumentoBusca(
        id=4,
        titulo="Setup Gamer no Quarto: Como aproveitar cada canto do espaço",
        icone="🖥️",
        categoria="Tecnologia & Setup",
        texto="Colocar a mesa em L no canto da parede ajuda a organizar os cabos, o monitor ultrawide e a iluminação LED sem ocupar o resto do quarto.",
    ),
    DocumentoBusca(
        id=5,
        titulo="Treino de Final de Semana: Quem joga em equipe evolui mais rápido",
        icone="⚽",
        categoria="Esportes & E-Sports",
        texto="Toda sexta eu jogo bola na quadra e depois a galera joga partidas ranqueadas online. O segredo é a comunicação rápida do time.",
    ),
    DocumentoBusca(
        id=6,
        titulo="Lançamento do Ano: O novo jogo de mundo aberto quebrou recordes",
        icone="🎮",
        categoria="Games",
        texto="Esse jogo mistura gráficos realistas com inteligência artificial avançada nos personagens, tornando cada missão única para os jogadores.",
    ),
    DocumentoBusca(
        id=7,
        titulo="Finanças na Adolescência: Como abrir sua primeira conta em banco digital",
        icone="💳",
        categoria="Finanças & Carreira",
        texto="Hoje qualquer estudante pode guardar dinheiro pelo aplicativo do banco, organizar gastos do mês e até dividir a conta da lanchonete.",
    ),
    DocumentoBusca(
        id=8,
        titulo="Amizade e Respeito: Quando eu banco o lanche da galera depois da prova",
        icone="🍔",
        categoria="Cotidiano",
        texto="Depois do simulado do vestibular, prometi que eu banco o açaí se todo mundo acertar as questões de matemática e redação.",
    ),
]


def buscar_documentos(consulta: str) -> Dict[str, object]:
    """
    Compara dois motores de Recuperação de Informação sobre a coleção de documentos:
    1. Busca Tradicional / Sem POS Tagging (usa palavras exatas ou radical cego RSLP):
       - Confunde homógrafos ("rio" verbo vs "rio" substantivo; "canto" verbo vs "canto" lugar; "banco" vs "bancar")
       - Ou perde conjugações verbais irregulares ("rio" -> "riram").
    2. Busca Inteligente com POS Tagging + Lematização Contextualizada:
       - Filtra seletivamente as Stop Words funcionais (CON, PRON, PUNCT)
       - Reduz cada termo ao seu lema correto segundo a classe gramatical
       - Faz o casamento pelo par (lema, classe), eliminando ambiguidade!
    """
    tokens_consulta = analisar_frase(consulta)
    termos_semanticos = [t for t in tokens_consulta if not t.eh_stopword]
    stopwords_removidas = [t for t in tokens_consulta if t.eh_stopword and t.classe != "PUNCT"]

    resultados_sem_pos = []
    resultados_com_pos = []

    palavras_brutas = {
        t.normalizado for t in tokens_consulta if t.classe != "PUNCT" and len(t.normalizado) > 2
    }
    stems_consulta = {
        t.stem_nltk for t in termos_semanticos
    }

    for doc in COLECAO_DOCUMENTOS:
        tokens_doc = analisar_frase(f"{doc.titulo}. {doc.texto}")

        # --- 1. Busca Sem POS Tagging (compara palavra exata ou radical RSLP sem classe gramatical) ---
        matches_brutos = []
        for t_d in tokens_doc:
            if t_d.classe == "PUNCT":
                continue
            if t_d.normalizado in palavras_brutas or (not t_d.eh_stopword and t_d.stem_nltk in stems_consulta):
                item_str = f"«{t_d.texto}» (radical: `{t_d.stem_nltk}`)"
                if item_str not in matches_brutos:
                    matches_brutos.append(item_str)

        if matches_brutos:
            resultados_sem_pos.append(
                {
                    "documento": doc,
                    "matches": matches_brutos,
                    "pontos": len(matches_brutos),
                }
            )

        # --- 2. Busca Com POS Tagging (compara Lema Contextual + Classe Gramatical) ---
        matches_pos = []
        for t_q in termos_semanticos:
            for t_d in tokens_doc:
                if t_d.lema == t_q.lema and t_d.classe == t_q.classe:
                    descricao = f"«{t_d.texto}» → `{t_d.lema}` ({POS_INFO[t_d.classe]['nome_curto']})"
                    if descricao not in matches_pos:
                        matches_pos.append(descricao)

        if matches_pos:
            resultados_com_pos.append(
                {
                    "documento": doc,
                    "matches": matches_pos,
                    "pontos": len(matches_pos),
                }
            )

    resultados_sem_pos.sort(key=lambda x: x["pontos"], reverse=True)
    resultados_com_pos.sort(key=lambda x: x["pontos"], reverse=True)

    return {
        "tokens_consulta": tokens_consulta,
        "termos_semanticos": termos_semanticos,
        "stopwords_removidas": stopwords_removidas,
        "resultados_sem_pos": resultados_sem_pos,
        "resultados_com_pos": resultados_com_pos,
    }
