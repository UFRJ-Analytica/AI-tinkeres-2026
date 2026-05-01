import streamlit as st
import requests
import pandas as pd

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
    uf_input = st.text_input("Filtrar por UF (Opcional):")
    if st.button("Executar GET"):
        params = {"uf": uf_input} if uf_input else {}
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
    col1, col2, col3 = st.columns(3)
    with col1:
        uf = st.text_input("UF:")
        safra = st.number_input("Ano da Safra:", value=0)
    with col2:
        municipio = st.text_input("Município:")
        solo = st.number_input("Cod Solo (1 a 3):", value=0)
    with col3:
        cultura = st.text_input("Cultura:")
        limite = st.number_input("Limite:", value=100)

    if st.button("Buscar Dados"):
        params = {"limite": limite}
        if uf: params["uf"] = uf
        if municipio: params["municipio"] = municipio
        if cultura: params["cultura"] = cultura
        if safra > 0: params["safra_ini"] = safra
        if solo > 0: params["cod_solo"] = solo
        
        dados, status = fetch_api("/api/zarc", params)
        if dados and dados.get("dados"):
            st.success(f"Registros encontrados: {dados.get('total')}")
            st.dataframe(pd.DataFrame(dados.get("dados")))

elif opcao == "Gerar Alerta de Risco":
    st.subheader("Teste: /api/alerta")
    col1, col2 = st.columns(2)
    with col1:
        geocodigo = st.text_input("Geocódigo (ex: 3550308):")
    with col2:
        ano = st.number_input("Ano:", min_value=2000, value=2023)
        solo = st.selectbox("Código Solo:", [1, 2, 3], index=2)

    if st.button("Analisar Risco"):
        if not geocodigo:
            st.warning("O geocodigo é obrigatório!")
        else:
            dados, status = fetch_api("/api/alerta", {"geocodigo": geocodigo, "ano": ano, "solo": solo})
            if dados and "status_historico" in dados:
                st.success(f"Análise: {dados['status_historico']}")
                st.json(dados)
            elif dados:
                st.warning(dados.get("status"))