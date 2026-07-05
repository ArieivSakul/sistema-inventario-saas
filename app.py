import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Inventário PRO", layout="wide", page_icon="🏢")

# --- CONEXÃO COM O BANCO DE DADOS ---
conn = sqlite3.connect('estoque_pro.db', check_same_thread=False)

# --- MENU LATERAL (NAVEGAÇÃO) ---
st.sidebar.title("🏢 Inventário PRO")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navegação", 
    ["📊 Dashboard Gerencial", "🔫 Operador (Scanner)", "📦 Gestão de Produtos"]
)
st.sidebar.markdown("---")
st.sidebar.caption("SaaS desenvolvido em Python")

# ==========================================
# TELA 1: DASHBOARD GERENCIAL
# ==========================================
if menu == "📊 Dashboard Gerencial":
    st.title("📊 Painel de Controle")
    st.markdown("Visão geral do estoque em tempo real.")

    df_produtos = pd.read_sql_query("SELECT * FROM produtos", conn)

    if not df_produtos.empty:
        total_skus = len(df_produtos)
        total_fisico = int(df_produtos['estoque_atual'].sum())
        
        itens_criticos = df_produtos[df_produtos['estoque_atual'] <= df_produtos['estoque_minimo']]
        qtd_criticos = len(itens_criticos)

        col1, col2, col3 = st.columns(3)
        col1.metric("SKUs Cadastrados", total_skus)
        col3.metric("Total de Itens Físicos", total_fisico)
        col2.metric("Alertas de Estoque", qtd_criticos, delta=f"{qtd_criticos} itens críticos", delta_color="inverse")

        st.divider()

        st.subheader("Níveis de Estoque por Produto")
        
        df_produtos['Status'] = df_produtos.apply(
            lambda x: 'Crítico' if x['estoque_atual'] <= x['estoque_minimo'] else 'OK', axis=1
        )
        
        fig = px.bar(
            df_produtos, 
            x='nome', 
            y='estoque_atual', 
            color='Status',
            color_discrete_map={'OK': '#00CC96', 'Crítico': '#EF553B'},
            text='estoque_atual',
            title="Quantidade Física vs Risco de Falta"
        )
        fig.update_layout(xaxis_title="Produto", yaxis_title="Quantidade em Estoque")
        
        st.plotly_chart(fig, use_container_width=True)

        if qtd_criticos > 0:
            st.warning("⚠️ Os seguintes itens precisam de reposição imediata:")
            st.dataframe(
                itens_criticos[['sku', 'nome', 'categoria', 'estoque_atual', 'estoque_minimo']], 
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("Nenhum produto cadastrado no banco de dados ainda.")

# ==========================================
# TELA 2: OPERADOR (SCANNER)
# ==========================================
elif menu == "🔫 Operador (Scanner)":
    st.title("🔫 Registro de Movimentação")
    st.markdown("Use o leitor de código de barras ou digite o SKU manualmente.")

    with st.form("form_scanner", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            sku_bipado = st.text_input("Bipe o Código (SKU) aqui:")
        
        with col2:
            tipo_mov = st.radio("Tipo de Movimentação:", ["ENTRADA", "SAIDA"], horizontal=True)

        qtd = st.number_input("Quantidade:", min_value=1, value=1)
        
        botao_registrar = st.form_submit_button("Registrar no Sistema")

    if botao_registrar and sku_bipado:
        cursor = conn.cursor()
        
        cursor.execute("SELECT nome, estoque_atual FROM produtos WHERE sku = ?", (sku_bipado,))
        produto = cursor.fetchone()

        if produto:
            nome_prod = produto[0]
            estoque_atual = produto[1]
            
            if tipo_mov == "ENTRADA":
                novo_estoque = estoque_atual + qtd
            else:
                novo_estoque = estoque_atual - qtd

            cursor.execute("UPDATE produtos SET estoque_atual = ? WHERE sku = ?", (novo_estoque, sku_bipado))

            data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO movimentacoes (sku, tipo, quantidade, data_hora, usuario) 
                VALUES (?, ?, ?, ?, ?)
            ''', (sku_bipado, tipo_mov, qtd, data_hora, "Operador_Galpao"))
            
            conn.commit()

            st.success(f"✅ SUCESSO! {tipo_mov} de {qtd}x {nome_prod} registrada. Novo estoque: {novo_estoque}")
        
        else:
            st.error(f"❌ ALERTA: O código '{sku_bipado}' não está cadastrado no sistema.")

# ==========================================
# TELA 3: GESTÃO (CADASTRO)
# ==========================================
elif menu == "📦 Gestão de Produtos":
    st.title("📦 Cadastro de Produtos")
    st.info("Em breve: Aqui o gerente poderá cadastrar novos SKUs e alterar limites mínimos de estoque.")