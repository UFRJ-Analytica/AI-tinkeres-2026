import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Testador de APIs - Zarc", layout="wide")
st.title("🚀 Painel de Testes da API")
st.markdown("Use este painel para disparar requisições para a sua FastAPI e visualizar os resultados do Postgres.")

BASE_URL = "http://localhost:8000"

st.sidebar.header("Navegação")
opcao = st.sidebar.radio("Selecione o Endpoint:", [
    "Health Check", "Listar UFs", "Listar Municípios", 
    "Listar Culturas", "Busca Completa (Zarc)", "Gerar Alerta de Risco"
])
st.divider()

def fetch_api(endpoint, params=None):
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json(), response.status_code
    except requests.exceptions.ConnectionError:
        st.error("❌ A FastAPI não está rodando. Ligue a API no terminal com 'uvicorn api:app --reload'")
        return None, None
    except requests.exceptions.HTTPError as err:
        st.error(f"❌ Erro na API (Status {response.status_code}): {response.text}")
        return None, response.status_code

# Funções de cache para não sobrecarregar a API toda vez que a tela recarregar
@st.cache_data(ttl=600)
def get_opcoes_uf():
    dados, _ = fetch_api("/api/filtros/ufs")
    return dados.get("dados", []) if dados else []

@st.cache_data(ttl=600)
def get_opcoes_municipios(uf=None):
    params = {"uf": uf} if uf and uf != "Todas" else {}
    dados, _ = fetch_api("/api/filtros/municipios", params)
    return dados.get("dados", []) if dados else []

@st.cache_data(ttl=600)
def get_opcoes_culturas():
    dados, _ = fetch_api("/api/filtros/culturas")
    return dados.get("dados", []) if dados else []


if opcao == "Health Check":
    st.subheader("Teste: /api/health")
    if st.button("Executar GET /api/health"):
        dados, status = fetch_api("/api/health")
        if dados:
            st.success(f"Status: {status}")
            st.json(dados)

elif opcao == "Listar UFs":
    st.subheader("Teste: /api/filtros/ufs")
    if st.button("Executar GET"):
        dados, status = fetch_api("/api/filtros/ufs")
        if dados:
            st.success(f"Total: {dados.get('total')}")
            st.dataframe(pd.DataFrame(dados.get('dados'), columns=["UFs"]))

elif opcao == "Listar Municípios":
    st.subheader("Teste: /api/filtros/municipios")
    lista_ufs = get_opcoes_uf()
    uf_input = st.selectbox("Filtrar por UF (Opcional):", ["Todas"] + lista_ufs)
    
    if st.button("Executar GET"):
        params = {"uf": uf_input} if uf_input != "Todas" else {}
        dados, status = fetch_api("/api/filtros/municipios", params)
        if dados:
            st.success(f"Total: {dados.get('total')}")
            st.dataframe(pd.DataFrame(dados.get('dados'), columns=["Municípios"]))

elif opcao == "Listar Culturas":
    st.subheader("Teste: /api/filtros/culturas")
    if st.button("Executar GET"):
        dados, status = fetch_api("/api/filtros/culturas")
        if dados:
            st.success(f"Total: {dados.get('total')}")
            st.dataframe(pd.DataFrame(dados.get('dados'), columns=["Culturas"]))

elif opcao == "Busca Completa (Zarc)":
    st.subheader("Teste: /api/zarc")
    
    # Carregando as listas dos filtros
    lista_ufs = get_opcoes_uf()
    lista_culturas = get_opcoes_culturas()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        uf = st.selectbox("UF:", ["Todas"] + lista_ufs)
        ano_ref = st.number_input("Ano de Referência:", value=0)
    
    with col2:
        # A lista de municípios muda dependendo da UF selecionada
        lista_municipios = get_opcoes_municipios(uf)
        municipio = st.selectbox("Município:", ["Todos"] + lista_municipios)
        solo = st.selectbox("Cod Solo:", [0, 1, 2, 3], index=0, format_func=lambda x: "Todos" if x == 0 else f"Tipo {x}")
        
    with col3:
        cultura = st.selectbox("Cultura:", ["Todas"] + lista_culturas)
        limite = st.number_input("Limite:", value=500, step=100)

    if st.button("Buscar e Analisar Dados"):
        params = {"limite": limite}
        if uf != "Todas": params["uf"] = uf
        if municipio != "Todos": params["municipio"] = municipio
        if cultura != "Todas": params["cultura"] = cultura
        if ano_ref > 0: params["ano_referencia"] = ano_ref
        if solo > 0: params["cod_solo"] = solo
        
        with st.spinner("Buscando dados e gerando gráficos..."):
            dados, status = fetch_api("/api/zarc", params)
            
        if dados and dados.get("dados"):
            st.success(f"Registros encontrados: {dados.get('total')}")
            df = pd.DataFrame(dados.get("dados"))
            
            # Criação de Abas para separar a visualização
            aba_graficos, aba_dados = st.tabs(["📊 Dashboards & Análises", "🗄️ Dados Brutos"])
            
            with aba_graficos:
                if 'decendio_id' in df.columns and 'risco_valor' in df.columns:
                    # Ordenação correta dos decêndios (extraindo o número de 'dec1', 'dec2'...)
                    df['dec_num'] = df['decendio_id'].str.extract(r'(\d+)').astype(float)
                    df_plot = df.sort_values('dec_num')
                    
                    # Gráfico 1: Risco por Decêndio (Linha)
                    fig_linha = px.line(
                        df_plot, x='decendio_id', y='risco_valor', color='cultura',
                        markers=True, title='Evolução do Risco Climático por Decêndio',
                        labels={'decendio_id': 'Período (Decêndio)', 'risco_valor': 'Risco (%)'}
                    )
                    st.plotly_chart(fig_linha, use_container_width=True)
                    
                    col_g1, col_g2 = st.columns(2)
                    with col_g1:
                        # Gráfico 2: Média de risco por Cultura
                        df_media = df_plot.groupby('cultura', as_index=False)['risco_valor'].mean()
                        fig_bar = px.bar(
                            df_media, x='cultura', y='risco_valor', color='cultura',
                            title='Média de Risco por Cultura',
                            labels={'cultura': 'Cultura', 'risco_valor': 'Risco Médio (%)'}
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)
                        
                    with col_g2:
                        # Gráfico 3: Distribuição do risco (Boxplot)
                        fig_box = px.box(
                            df_plot, x='cod_solo', y='risco_valor', color='cod_solo',
                            title='Distribuição do Risco por Tipo de Solo',
                            labels={'cod_solo': 'Código do Solo', 'risco_valor': 'Risco (%)'}
                        )
                        # Transformando cod_solo em string para o Plotly tratar como categoria
                        fig_box.update_xaxes(type='category')
                        st.plotly_chart(fig_box, use_container_width=True)
                else:
                    st.info("As colunas 'decendio_id' e 'risco_valor' precisam estar presentes no banco para gerar os gráficos.")

            with aba_dados:
                st.dataframe(df.drop(columns=['dec_num'], errors='ignore'))

elif opcao == "Gerar Alerta de Risco":
    st.subheader("Teste: /api/alerta")
    col1, col2 = st.columns(2)
    with col1:
        geocodigo = st.text_input("Geocódigo (ex: 3550308):")
    with col2:
        ano_ref = st.number_input("Ano de Referência:", min_value=2000, value=2023)
        solo = st.selectbox("Código Solo:", [1, 2, 3], index=2)

    if st.button("Analisar Risco"):
        if not geocodigo:
            st.warning("O geocodigo é obrigatório!")
        else:
            params = {
                "geocodigo": geocodigo, 
                "ano_referencia": ano_ref, 
                "cod_solo": solo
            }
            dados, status = fetch_api("/api/alerta", params)
            
            if dados and "status_historico" in dados:
                if "Aceitável" in dados['status_historico']:
                    st.success(f"Análise: {dados['status_historico']}")
                else:
                    st.error(f"Análise: {dados['status_historico']}")
                st.json(dados)
            elif dados:
                st.warning(dados.get("status"))