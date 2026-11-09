import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da Página
st.set_page_config(
    page_title="ReforAMAR - Gestão e Impacto Social",
    page_icon="🏠",
    layout="wide"
)

# Inicialização de dados simulados no Session State (para persistência na sessão)
if "familias" not in st.session_state:
    st.session_state.familias = pd.DataFrame([
        {
            "ID": 1,
            "Nome": "Maria da Silva",
            "Bairro": "Pajuçara",
            "Criancas": 3,
            "Idosos": 1,
            "Infiltracao_Grave": True,
            "Risco_Eletrico": True,
            "Status": "Em Obra",
            "Prioridade": "Alta"
        },
        {
            "ID": 2,
            "Nome": "João Oliveira",
            "Bairro": "Redinha",
            "Criancas": 1,
            "Idosos": 0,
            "Infiltracao_Grave": True,
            "Risco_Eletrico": False,
            "Status": "Triagem",
            "Prioridade": "Média"
        }
    ])

if "estoque" not in st.session_state:
    st.session_state.estoque = pd.DataFrame([
        {"Material": "Sacos de Cimento (50kg)", "Quantidade": 45, "Unidade": "sacos"},
        {"Material": "Tijolos 8 furos", "Quantidade": 1200, "Unidade": "unidades"},
        {"Material": "Latas de Tinta Branca (18L)", "Quantidade": 8, "Unidade": "latas"},
        {"Material": "Disjuntores 30A", "Quantidade": 15, "Unidade": "unidades"}
    ])

# Menu Lateral
st.sidebar.title("🏠 ReforAMAR - Gestão")
menu = st.sidebar.selectbox(
    "Navegação", 
    ["📊 Dashboard Geral", "📋 Cadastro e Triagem", "📦 Gestão de Estoque", "📱 Portal Pós-Obra (Família)"]
)

# ---------------------------------------------------------
# 1. DASHBOARD GERAL
# ---------------------------------------------------------
if menu == "📊 Dashboard Geral":
    st.title("📊 Painel de Impacto e Gestão")
    st.markdown("Visão consolidada das operações da ReforAMAR.")

    col1, col2, col3, col4 = st.columns(4)
    df_f = st.session_state.familias
    df_e = st.session_state.estoque

    total_familias = len(df_f)
    obras_concluidas = len(df_f[df_f["Status"] == "Entregue"])
    obras_andamento = len(df_f[df_f["Status"] == "Em Obra"])
    total_materiais = df_e["Quantidade"].sum()

    col1.metric("Famílias Cadastradas", total_familias)
    col2.metric("Obras em Andamento", obras_andamento)
    col3.metric("Obras Entregues", obras_concluidas)
    col4.metric("Insumos em Estoque", f"{total_materiais} itens")

    st.divider()
    st.subheader("Famílias por Nível de Urgência")
    if not df_f.empty:
        st.bar_chart(df_f["Prioridade"].value_counts())
    else:
        st.info("Nenhum dado cadastrado ainda.")

# ---------------------------------------------------------
# 2. CADASTRO E TRIAGEM
# ---------------------------------------------------------
elif menu == "📋 Cadastro e Triagem":
    st.title("📋 Cadastro de Famílias e Matriz de Urgência")
    st.markdown("Insira uma nova família para calcular automaticamente a prioridade habitacional.")

    with st.form("form_familia"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Responsável")
            bairro = st.text_input("Bairro / Comunidade")
            criancas = st.number_input("Número de Crianças na Casa", min_value=0, step=1)
        with col2:
            idosos = st.number_input("Número de Idosos na Casa", min_value=0, step=1)
            infiltracao = st.checkbox("Possui infiltração grave / telhado quebrado?")
            risco_eletrico = st.checkbox("Possui fiação exposta / risco elétrico?")
            status = st.selectbox("Status Atual", ["Triagem", "Projeto", "Em Obra", "Entregue"])

        submitted = st.form_submit_button("Cadastrar e Calcular Urgência")
        if submitted:
            # Algoritmo simples de pontuação de urgência
            pontos = (criancas * 1) + (idosos * 2) + (3 if infiltracao else 0) + (3 if risco_eletrico else 0)
            if pontos >= 6:
                prioridade = "Alta"
            elif pontos >= 3:
                prioridade = "Média"
            else:
                prioridade = "Baixa"

            novo_id = len(st.session_state.familias) + 1
            nova_linha = {
                "ID": novo_id, "Nome": nome, "Bairro": bairro, 
                "Criancas": criancas, "Idosos": idosos, 
                "Infiltracao_Grave": infiltracao, "Risco_Eletrico": risco_eletrico,
                "Status": status, "Prioridade": prioridade
            }
            st.session_state.familias = pd.concat([st.session_state.familias, pd.DataFrame([nova_linha])], ignore_index=True)
            st.success(f"Família cadastrada com sucesso! Prioridade calculada: **{prioridade}**")

    st.divider()
    st.subheader("Lista de Famílias Registradas")
    st.dataframe(st.session_state.familias, use_container_width=True)

# ---------------------------------------------------------
# 3. GESTÃO DE ESTOQUE
# ---------------------------------------------------------
elif menu == "📦 Gestão de Estoque":
    st.title("📦 Controle de Materiais e Doações")
    st.markdown("Gerencie o estoque de insumos de construção civil.")

    st.dataframe(st.session_state.estoque, use_container_width=True)

    with st.form("form_estoque"):
        st.subheader("Atualizar ou Adicionar Material")
        mat_nome = st.text_input("Nome do Material")
        mat_qtd = st.number_input("Quantidade", min_value=0, step=1)
        mat_un = st.text_input("Unidade (ex: sacos, unidades, metros)")
        
        btn_est = st.form_submit_button("Salvar no Estoque")
        if btn_est:
            # Verifica se já existe
            df_est = st.session_state.estoque
            if mat_nome in df_est["Material"].values:
                df_est.loc[df_est["Material"] == mat_nome, "Quantidade"] += mat_qtd
                st.success(f"Estoque de {mat_nome} atualizado!")
            else:
                novo_mat = {"Material": mat_nome, "Quantidade": mat_qtd, "Unidade": mat_un}
                st.session_state.estoque = pd.concat([df_est, pd.DataFrame([novo_mat])], ignore_index=True)
                st.success(f"Novo material {mat_nome} cadastrado!")

# ---------------------------------------------------------
# 4. PORTAL PÓS-OBRA (FAMÍLIA)
# ---------------------------------------------------------
elif menu == "📱 Portal Pós-Obra (Família)":
    st.title("📱 Portal do Beneficiário (Pós-Obra)")
    st.markdown("Simulação da interface leve acessada pelo celular do morador após a entrega da reforma.")

    st.info("👋 Olá, bem-vindo(a) ao seu canal direto com a ReforAMAR!")
    
    tab1, tab2 = st.tabs(["💡 Dicas de Manutenção Preventiva", "🛠️ Solicitar Suporte Pós-Obra"])

    with tab1:
        st.subheader("Cuidados com a sua nova casa:")
        st.markdown("""
        - **Limpeza do Telhado e Calhas:** Limpe folhas a cada 3 meses para evitar entupimentos e infiltrações.
        - **Instalações Elétricas:** Evite sobrecarregar tomadas com muitos "benjamins" (Ts).
        - **Pintura e Umidade:** Mantenha as janelas abertas durante o dia para garantir a ventilação cruzada e evitar mofo.
        """)

    with tab2:
        st.subheader("Precisa de um reparo urgente?")
        with st.form("form_chamado"):
            fam_nome = st.text_input("Seu Nome Completo")
            problema = st.text_area("Descreva o problema (ex: vazamento no cano do banheiro)")
            enviar_ch = st.form_submit_button("Enviar Chamado para a Equipe")
            if enviar_ch:
                st.success("Chamado enviado com sucesso! A equipe técnica da ReforAMAR entrará em contato em breve.")