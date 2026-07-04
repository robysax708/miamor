import re
import unicodedata

import streamlit as st

# ============================================================
# CONFIGURE AQUI AS RESPOSTAS CORRETAS
# ============================================================
ANSWERS = {
    1: "eu te amo desde o gira gira",
    2: "sempre foi meu sonho desde pequena",
    "3a": "10/01",
    "3b": "parque taquaral",
}

FINALE_TEXT = (
    'Toda essa investigação era só um jeito de dizer: eu presto atenção em cada '
    'detalhe seu — desde o "gira gira" até o sonho que você carrega desde pequena.'
    '<br><br>O presente é uma <b>Instax Mini 12 da Fujifilm, rosa</b> — pra gente '
    'registrar os próximos capítulos em Polaroid.'
    '<br><br>Te espero no <b>Parque Taquaral</b>, dia <b>10/01</b>. '
    'Feliz aniversário, detetive. 📸💗'
)

# ============================================================
# CIFRA PIGPEN (geração dos símbolos em SVG)
# ============================================================
G1, G2, G3, G4 = "ABCDEFGHI", "JKLMNOPQR", "STUV", "WXYZ"


def tic_path(idx: int, with_dot: bool) -> str:
    r, c = divmod(idx, 3)
    x0, y0 = c * 10, r * 10
    lines = []
    if c > 0:
        lines.append(f"M{x0},{y0} L{x0},{y0 + 10}")
    if c < 2:
        lines.append(f"M{x0 + 10},{y0} L{x0 + 10},{y0 + 10}")
    if r > 0:
        lines.append(f"M{x0},{y0} L{x0 + 10},{y0}")
    if r < 2:
        lines.append(f"M{x0},{y0 + 10} L{x0 + 10},{y0 + 10}")
    dot = f'<circle cx="{x0 + 5}" cy="{y0 + 5}" r="1.7" fill="currentColor"/>' if with_dot else ""
    return f'<path d="{" ".join(lines)}" stroke="currentColor" stroke-width="2.4" fill="none" stroke-linecap="round"/>{dot}'


def x_path(idx: int, with_dot: bool) -> str:
    dirs = ["top", "right", "bottom", "left"]
    d = dirs[idx]
    TL, TR, BR, BL, CT = (0, 0), (30, 0), (30, 30), (0, 30), (15, 15)
    if d == "top":
        p1, p2, dot_pos = TL, TR, (15, 8)
    elif d == "right":
        p1, p2, dot_pos = TR, BR, (22, 15)
    elif d == "bottom":
        p1, p2, dot_pos = BR, BL, (15, 22)
    else:
        p1, p2, dot_pos = BL, TL, (8, 15)
    dot = f'<circle cx="{dot_pos[0]}" cy="{dot_pos[1]}" r="1.7" fill="currentColor"/>' if with_dot else ""
    return (
        f'<path d="M{p1[0]},{p1[1]} L{CT[0]},{CT[1]} L{p2[0]},{p2[1]}" '
        f'stroke="currentColor" stroke-width="2.4" fill="none" '
        f'stroke-linecap="round" stroke-linejoin="round"/>{dot}'
    )


def path_for_letter(letter: str) -> str:
    letter = letter.upper()
    if letter in G1:
        return tic_path(G1.index(letter), False)
    if letter in G2:
        return tic_path(G2.index(letter), True)
    if letter in G3:
        return x_path(G3.index(letter), False)
    if letter in G4:
        return x_path(G4.index(letter), True)
    return ""


def symbol_block(letter: str, show_label: bool = False, size: int = 34) -> str:
    p = path_for_letter(letter)
    label = (
        f'<div style="text-align:center;font-family:\'Courier New\',monospace;'
        f'font-size:11px;margin-top:2px;color:#2a2115;">{letter}</div>'
        if show_label
        else ""
    )
    return (
        f'<div style="text-align:center;">'
        f'<svg viewBox="0 0 30 30" width="{size}" height="{size}" style="color:#2a2115;">{p}</svg>'
        f"{label}</div>"
    )


def pigpen_key_html() -> str:
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return (
        '<div style="display:flex;flex-wrap:wrap;gap:8px;">'
        + "".join(symbol_block(l, True, 30) for l in alphabet)
        + "</div>"
    )


def pigpen_message_html(msg: str, size: int = 44) -> str:
    parts = []
    for ch in msg.upper():
        if ch == " ":
            parts.append('<div style="width:16px;"></div>')
        else:
            parts.append(symbol_block(ch, False, size))
    return '<div style="display:flex;flex-wrap:wrap;gap:14px;align-items:center;">' + "".join(parts) + "</div>"


def reverse_str(s: str) -> str:
    return s[::-1]


def normalize(s: str) -> str:
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s


# ============================================================
# ESTADO
# ============================================================
st.set_page_config(page_title="O Enigma do Aniversário", page_icon="🔎", layout="centered")

if "stage" not in st.session_state:
    st.session_state.stage = 1  # etapa atual destravada
if "celebrated" not in st.session_state:
    st.session_state.celebrated = False

# ============================================================
# ESTILO
# ============================================================
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(ellipse at center, #15120d 0%, #0b0906 100%);
    }
    .case-label {
        font-family: 'Courier New', monospace;
        letter-spacing: 3px;
        text-transform: uppercase;
        font-size: 12px;
        color: #b8924f;
        text-align: center;
    }
    .case-title {
        font-family: Georgia, serif;
        font-size: 34px;
        font-weight: bold;
        color: #ece2c8;
        text-align: center;
        margin: 4px 0;
    }
    .case-sub {
        color: #a89a7c;
        font-style: italic;
        font-size: 15px;
        text-align: center;
        margin-bottom: 28px;
    }
    .dossie-card {
        background: #ece2c8;
        color: #2a2115;
        border-radius: 4px;
        padding: 26px 28px 10px 28px;
        margin-bottom: 6px;
        box-shadow: 0 14px 30px rgba(0,0,0,0.5);
    }
    .stage-eyebrow {
        font-family: 'Courier New', monospace;
        font-size: 12px;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #7c2323;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .stage-heading {
        font-family: Georgia, serif;
        font-size: 22px;
        margin: 0 0 12px;
        color: #2a2115;
    }
    .clue-text {
        font-family: 'Courier New', monospace;
        background: #c9bb96;
        border-left: 3px solid #7c2323;
        padding: 14px 16px;
        font-size: 15px;
        line-height: 1.7;
        margin-bottom: 14px;
        white-space: pre-wrap;
    }
    .locked-box {
        background: #221c15;
        color: #8a7d63;
        border-radius: 4px;
        padding: 18px 22px;
        text-align: center;
        font-family: 'Courier New', monospace;
        margin-bottom: 20px;
        border: 1px dashed #4a4030;
    }
    .finale-box {
        background: #ece2c8;
        color: #2a2115;
        border-radius: 4px;
        padding: 34px 30px;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0,0,0,0.55);
    }
    .finale-title {
        font-family: Georgia, serif;
        font-size: 24px;
        color: #b8924f;
        margin-bottom: 14px;
    }
    .finale-text {
        font-size: 17px;
        line-height: 1.6;
        color: #2a2115;
    }
    div[data-testid="stTextInput"] input {
        font-family: 'Courier New', monospace;
        background: #fffbf0 !important;
        color: #2a2115 !important;
        border: 1px solid #6b5f47 !important;
    }
    div.stButton > button {
        font-family: Georgia, serif;
        letter-spacing: 1px;
        text-transform: uppercase;
        background: #7c2323;
        color: #f4ead2;
        border: none;
        border-radius: 2px;
    }
    div.stButton > button:hover {
        background: #a63333;
        color: #f4ead2;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# CABEÇALHO
# ============================================================
st.markdown('<div class="case-label">Arquivo Confidencial &middot; Caso Nº 14.07</div>', unsafe_allow_html=True)
st.markdown('<div class="case-title">O Enigma do Aniversário</div>', unsafe_allow_html=True)
st.markdown('<div class="case-sub">3 pistas. 1 verdade. Um presente esperando para ser encontrado.</div>', unsafe_allow_html=True)

# ============================================================
# ETAPA 1 — ESPELHO
# ============================================================
st.markdown('<div class="dossie-card">', unsafe_allow_html=True)
st.markdown('<div class="stage-eyebrow">Etapa I &middot; A Pista do Espelho</div>', unsafe_allow_html=True)
st.markdown('<div class="stage-heading">Nem tudo que se lê é o que parece</div>', unsafe_allow_html=True)
st.write("Pegue o envelope que você recebeu. Decifre o que está escrito nele e digite a resposta abaixo.")
with st.expander("preciso de uma pista"):
    st.write("Leonardo da Vinci escrevia assim para proteger seus segredos. Um espelho (ou a câmera frontal do celular) resolve.")

if st.session_state.stage == 1:
    with st.form("form1", clear_on_submit=False):
        resp1 = st.text_input("Resposta decifrada", key="input1", label_visibility="collapsed", placeholder="Digite a resposta decifrada...")
        ok1 = st.form_submit_button("Decifrar")
    if ok1:
        if normalize(resp1) == normalize(ANSWERS[1]):
            st.session_state.stage = 2
            st.rerun()
        else:
            st.error("Isso não confere com as evidências. Olhe de novo o envelope.")
else:
    st.success("✓ Decifrado")
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# ETAPA 2 — SÍMBOLOS
# ============================================================
if st.session_state.stage >= 2:
    st.markdown('<div class="dossie-card">', unsafe_allow_html=True)
    st.markdown('<div class="stage-eyebrow">Etapa II &middot; O Código dos Símbolos</div>', unsafe_allow_html=True)
    st.markdown('<div class="stage-heading">Uma letra, uma forma</div>', unsafe_allow_html=True)
    st.write("Cada símbolo abaixo representa uma letra. Use a chave para decifrar a mensagem e descubra onde está o próximo envelope.")
    st.markdown(f'<div class="clue-text">{pigpen_key_html()}</div>', unsafe_allow_html=True)
    st.write("Mensagem cifrada:")
    st.markdown(f'<div class="clue-text">{pigpen_message_html(reverse_str(ANSWERS[2]))}</div>', unsafe_allow_html=True)
    with st.expander("preciso de uma pista"):
        st.write("Compare o formato e a posição de cada símbolo com a chave acima. Se tiver um pontinho no meio, é uma letra do segundo grupo.")

    if st.session_state.stage == 2:
        with st.form("form2", clear_on_submit=False):
            resp2 = st.text_input("Resposta", key="input2", label_visibility="collapsed", placeholder="Onde está escondida a próxima pista?")
            ok2 = st.form_submit_button("Revelar")
        if ok2:
            if normalize(resp2) == normalize(ANSWERS[2]):
                st.session_state.stage = 3
                st.rerun()
            else:
                st.error("Ainda não é isso. Confira símbolo por símbolo.")
    else:
        st.success("✓ Decifrado")
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown('<div class="locked-box">🔒 Decifrem a Etapa I para destravar</div>', unsafe_allow_html=True)

# ============================================================
# ETAPA 3 — MISTO (NÚMEROS + LETRAS)
# ============================================================
if st.session_state.stage >= 3:
    st.markdown('<div class="dossie-card">', unsafe_allow_html=True)
    st.markdown('<div class="stage-eyebrow">Etapa III &middot; O Código Final</div>', unsafe_allow_html=True)
    st.markdown('<div class="stage-heading">Números e letras, juntos</div>', unsafe_allow_html=True)
    st.write(
        "Este envelope tem dois códigos. Um usa números (linha e coluna formam uma letra), "
        "o outro usa letras (a posição dela no alfabeto forma um número: A=1, B=2... Z=26). "
        "Decifrem os dois para encerrar o caso."
    )
    tabela = (
        "Tabela (linha,coluna):\n"
        "A=11 B=12 C=13 D=14 E=15\n"
        "F=21 G=22 H=23 I=24 J=25\n"
        "K=31 L=32 M=33 N=34 O=35\n"
        "P=41 Q=42 R=43 S=44 T=45\n"
        "U=51 V=52 W=53 X=54 Y=55  Z=(sem par, use 00)"
    )
    st.markdown(f'<div class="clue-text">{tabela}</div>', unsafe_allow_html=True)
    with st.expander("preciso de uma pista"):
        st.write("No código numérico, separe os números de dois em dois. No código de letras, cada letra sozinha é um número.")

    st.write("Código em letras (revela uma data):")
    st.markdown('<div class="clue-text" style="text-align:center; font-size:22px; letter-spacing:6px;">J &nbsp; A</div>', unsafe_allow_html=True)

    st.write("Código em números (revela um local):")
    st.markdown(
        '<div class="clue-text" style="text-align:center; font-size:18px; letter-spacing:2px;">'
        "41 11 43 42 51 15 / 45 11 42 51 11 43 11 32</div>",
        unsafe_allow_html=True,
    )

    if st.session_state.stage == 3:
        with st.form("form3", clear_on_submit=False):
            resp3a = st.text_input("Data decifrada", placeholder="Digite a data decifrada (ex: 00/00)...")
            resp3b = st.text_input("Local decifrado", placeholder="Digite o local decifrado...")
            ok3 = st.form_submit_button("Abrir o presente")
        if ok3:
            if normalize(resp3a) == normalize(ANSWERS["3a"]) and normalize(resp3b) == normalize(ANSWERS["3b"]):
                st.session_state.stage = 4
                st.rerun()
            else:
                st.error("Algo ainda não fechou. Confira os dois códigos com calma.")
    else:
        st.success("✓ Decifrado")
    st.markdown("</div>", unsafe_allow_html=True)
elif st.session_state.stage == 2:
    st.markdown('<div class="locked-box">🔒 Decifrem a Etapa II para destravar</div>', unsafe_allow_html=True)

# ============================================================
# FINAL
# ============================================================
if st.session_state.stage >= 4:
    st.markdown(
        f"""
        <div class="finale-box">
            <div style="font-size:56px;">📸</div>
            <div class="finale-title">Caso encerrado.</div>
            <div class="finale-text">{FINALE_TEXT}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not st.session_state.celebrated:
        st.balloons()
        st.session_state.celebrated = True
elif st.session_state.stage == 3:
    st.markdown('<div class="locked-box">🔒 Decifrem a Etapa III para revelar o presente</div>', unsafe_allow_html=True)
