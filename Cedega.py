import streamlit as st

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Project Cedega | Blackjack Sniper",
    page_icon="♠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONSTANTES DO SISTEMA ---
TOTAL_BARALHOS = 8
TOTAL_CARTAS = TOTAL_BARALHOS * 52

# --- INICIALIZAÇÃO DO ESTADO (SESSION STATE) ---
def init_state():
    if 'banca' not in st.session_state: st.session_state.banca = 100
    if 'running_count' not in st.session_state: st.session_state.running_count = 0
    if 'cartas_vistas' not in st.session_state: st.session_state.cartas_vistas = 0

init_state()

# --- LÓGICA DE DECISÃO MATEMÁTICA (GTO) ---
def calcular_acao(tipo_mao: str, mao: str, dealer: str) -> tuple:
    dealer_val = 11 if dealer == 'A' else int(dealer)
    
    if tipo_mao == "Mão Dura (Hard)":
        mao_val = int(mao)
        if mao_val <= 8: return "🟢 PEDIR", "success"
        if mao_val == 9: return ("🔵 DOBRAR" if 3 <= dealer_val <= 6 else "🟢 PEDIR"), "info"
        if mao_val == 10: return ("🔵 DOBRAR" if 2 <= dealer_val <= 9 else "🟢 PEDIR"), "info"
        if mao_val == 11: return ("🔵 DOBRAR" if 2 <= dealer_val <= 10 else "🟢 PEDIR"), "info"
        if mao_val == 12: return ("🔴 PARAR" if 4 <= dealer_val <= 6 else "🟢 PEDIR"), "error"
        if 13 <= mao_val <= 16: return ("🔴 PARAR" if 2 <= dealer_val <= 6 else "🟢 PEDIR"), "error"
        if mao_val >= 17: return "🔴 PARAR", "error"

    elif tipo_mao == "Mão Macia (Soft)":
        if mao in ["A+2", "A+3"]: return ("🔵 DOBRAR" if 5 <= dealer_val <= 6 else "🟢 PEDIR"), "info"
        if mao in ["A+4", "A+5"]: return ("🔵 DOBRAR" if 4 <= dealer_val <= 6 else "🟢 PEDIR"), "info"
        if mao == "A+6": return ("🔵 DOBRAR" if 3 <= dealer_val <= 6 else "🟢 PEDIR"), "info"
        if mao == "A+7":
            if 3 <= dealer_val <= 6: return "🔵 DOBRAR", "info"
            if dealer_val in [2, 7, 8]: return "🔴 PARAR", "error"
            return "🟢 PEDIR", "success"
        if mao in ["A+8", "A+9", "A+10"]: return "🔴 PARAR", "error"

    elif tipo_mao == "Pares":
        if mao in ["A+A", "8+8"]: return "🟡 DIVIDIR", "warning"
        if mao == "10+10": return "🔴 PARAR", "error"
        if mao == "9+9": return ("🟡 DIVIDIR" if dealer_val in [2,3,4,5,6,8,9] else "🔴 PARAR"), "warning"
        if mao == "7+7": return ("🟡 DIVIDIR" if 2 <= dealer_val <= 7 else "🟢 PEDIR"), "warning"
        if mao == "6+6": return ("🟡 DIVIDIR" if 2 <= dealer_val <= 6 else "🟢 PEDIR"), "warning"
        if mao == "5+5": return ("🔵 DOBRAR" if 2 <= dealer_val <= 9 else "🟢 PEDIR"), "info"
        if mao == "4+4": return "🟢 PEDIR", "success"
        if mao in ["2+2", "3+3"]: return ("🟡 DIVIDIR" if 4 <= dealer_val <= 7 else "🟢 PEDIR"), "warning"

    return "ERRO DE LEITURA", "error"

# --- FUNÇÕES DE CONTROLE ---
def atualizar_contagem(valor: int):
    st.session_state.running_count += valor
    st.session_state.cartas_vistas += 1

def resetar_sapato():
    st.session_state.running_count = 0
    st.session_state.cartas_vistas = 0

# --- CÁLCULO DE VANTAGEM (TRUE COUNT) ---
baralhos_restantes = max(1.0, (TOTAL_CARTAS - st.session_state.cartas_vistas) / 52.0)
true_count = st.session_state.running_count / baralhos_restantes

# --- INTERFACE PRINCIPAL ---
st.title("♠️ PROJECT CEDEGA | OPERATION SNIPER")
st.markdown("Sistema de Extração de Vantagem Matemática (Advantage Play) - Módulo Hit & Run")

# --- EXPANDER DE REGRAS (PARA O EXECUTOR) ---
with st.expander("📖 REGRAS DE ENGAJAMENTO (LEITURA OBRIGATÓRIA ANTES DO START)", expanded=False):
    st.markdown("""
    **1. FASE DE ESPERA (WONGING):** Não aposte R$ 1 sequer enquanto o gatilho estiver Verde ou Amarelo. Deixe a mesa sangrar.
    **2. O BOTE:** Quando a tela gritar Laranja (+3) ou Vermelho (+4), entre rasgando com a aposta indicada.
    **3. DISCIPLINA CEGA:** A matemática não tem sentimento. Se a máquina mandar pedir com 16, você pede.
    **4. HIT AND RUN:** Bateu o saldo de R$ 200 (100% de lucro)? Fecha a aba, solicita o saque e a noite acabou.
    """)

st.markdown("---")

# --- PAINEL DE CONTROLE SUPERIOR (DASHBOARD) ---
col_dash1, col_dash2, col_dash3, col_dash4 = st.columns(4)
col_dash1.metric("Banca Atual", f"R$ {st.session_state.banca:.2f}")
col_dash2.metric("True Count (Precisão)", f"{true_count:.2f}")
col_dash3.metric("Running Count", st.session_state.running_count)
col_dash4.metric("Cartas no Lixo", f"{st.session_state.cartas_vistas} / {TOTAL_CARTAS}")

st.markdown("---")

# --- DIVISÃO DA TELA: GESTÃO E OPERAÇÃO ---
col_left, col_right = st.columns([1, 1.5], gap="large")

with col_left:
    st.subheader("🏦 Gestão da Banca")
    
    # Validação de quebra ou meta
    if st.session_state.banca >= 200:
        st.success("🏆 META ATINGIDA (R$ 200). FECHE A MESA E SAQUE IMEDIATAMENTE.")
    elif st.session_state.banca <= 0:
        st.error("💀 BANCA ZERADA. Fim da operação.")
    
    col_ganho, col_perda = st.columns(2)
    valor_op = st.number_input("Valor da última aposta (R$):", min_value=1, value=25, step=5)
    
    with col_ganho:
        if st.button("🟢 WIN (Ganhou)", use_container_width=True):
            st.session_state.banca += valor_op
            st.rerun()
        if st.button("🌟 BJ NATURAL (1.5x)", use_container_width=True):
            st.session_state.banca += (valor_op * 1.5)
            st.rerun()
            
    with col_perda:
        if st.button("🔴 LOSS (Perdeu)", use_container_width=True):
            st.session_state.banca -= valor_op
            st.rerun()
            
    st.markdown("---")
    st.subheader("🃏 Ação do App")
    
    col_tipo, col_mao, col_dlr = st.columns([1.5, 1, 1])
    with col_tipo:
        tipo_mao = st.selectbox("Tipo:", ["Mão Dura (Hard)", "Mão Macia (Soft)", "Pares"])
    with col_mao:
        if tipo_mao == "Mão Dura (Hard)": opcoes = [str(i) for i in range(4, 21)]
        elif tipo_mao == "Mão Macia (Soft)": opcoes = ["A+2", "A+3", "A+4", "A+5", "A+6", "A+7", "A+8", "A+9"]
        else: opcoes = ["A+A", "10+10", "9+9", "8+8", "7+7", "6+6", "5+5", "4+4", "3+3", "2+2"]
        mao_jogador = st.selectbox("Sua:", opcoes)
    with col_dlr:
        carta_dealer = st.selectbox("DLR:", [str(i) for i in range(2, 11)] + ["A"])

    acao, tipo_alerta = calcular_acao(tipo_mao, mao_jogador, carta_dealer)
    
    # Exibição da ação com cores nativas do Streamlit
    if tipo_alerta == "success": st.success(f"### 🎯 {acao}")
    elif tipo_alerta == "error": st.error(f"### 🛑 {acao}")
    elif tipo_alerta == "warning": st.warning(f"### 🔀 {acao}")
    else: st.info(f"### ⏫ {acao}")

with col_right:
    st.subheader("⏱️ Rastreador do Baralho (Clique Rápido)")
    
    # Botões gigantes para facilitar o clique
    c_baixa, c_neutra, c_alta = st.columns(3)
    with c_baixa:
        if st.button("⬇️ BAIXA (2-6)\n\n+1", use_container_width=True, type="primary"): 
            atualizar_contagem(1)
            st.rerun()
    with c_neutra:
        if st.button("➖ NEUTRA (7-9)\n\n 0", use_container_width=True, type="secondary"): 
            atualizar_contagem(0)
            st.rerun()
    with c_alta:
        if st.button("⬆️ ALTA (10-A)\n\n-1", use_container_width=True, type="primary"): 
            atualizar_contagem(-1)
            st.rerun()
            
    st.markdown("---")
    
    st.subheader("🚨 GATILHO DE ENGAJAMENTO")
    if true_count >= 4:
        st.error("## 🔥 STATUS: EXTREMO (+4)\n### 💰 ORDEM: APOSTAR R$ 50 (ALL-IN TÁTICO)")
    elif true_count >= 3:
        st.warning("## 🟠 STATUS: QUENTE (+3)\n### 💰 ORDEM: APOSTAR R$ 25 (BOTE)")
    elif true_count >= 2:
        st.info("## 🟡 STATUS: MORNO (+2)\n### 💰 ORDEM: R$ 0 (PREPARAR GATILHO)")
    else:
        st.success("## 🟢 STATUS: FRIO/NEUTRO\n### 💰 ORDEM: R$ 0 (APENAS OBSERVE)")
        
    st.markdown("---")
    if st.button("🔄 CARTA VERMELHA (RESETAR SAPATO)", use_container_width=True):
        resetar_sapato()
        st.rerun()
