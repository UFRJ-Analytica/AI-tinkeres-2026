Aqui está a sua documentação atualizada! Ela agora reflete todas as novas nomenclaturas (`ano_referencia`, `cod_solo`, `risco_valor`, etc.), a nova lógica de risco (onde valores menores ou iguais a 40% são aceitáveis) e inclui uma seção especial explicando o conceito de decêndios para quem for ler e consumir a sua API.

Você pode salvar este conteúdo como o seu arquivo **`README.md`**.

---

# 📖 Documentação da API: SafraViva (Zarc - PostgreSQL)

Esta API fornece acesso rápido e parametrizado aos dados do Zoneamento Agrícola de Risco Climático (Zarc) armazenados no banco de dados PostgreSQL. Os dados passaram por um processo de ETL rigoroso (Camadas Bronze, Silver e Gold) para otimizar as consultas e análises temporais.

*   **Base URL (Local):** `http://localhost:8000`
*   **Formato de Resposta:** `application/json`
*   **Interface Interativa (Swagger):** Disponível em `http://localhost:8000/docs`

---

## 🧠 Entendendo os Dados: O que são Decêndios?

Para consumir esta API corretamente, é essencial entender como o tempo é medido no Zarc.

**Os Decêndios (dec1 a dec36)**
A palavra "decêndio" significa um período de **10 dias**.
O ZARC não avalia o risco de plantar "em janeiro", porque plantar no dia 1º de janeiro ou no dia 30 pode ter riscos climáticos completamente diferentes. Ele divide o ano em blocos de 10 dias:

*   Como um mês tem (em média) 30 dias, temos **3 decêndios por mês**.
*   12 meses × 3 decêndios = **36 decêndios no ano** (do `dec1` ao `dec36`).
    *   `dec1`: 1 a 10 de Janeiro
    *   `dec2`: 11 a 20 de Janeiro
    *   ...
    *   `dec36`: 21 a 31 de Dezembro

**O que o Risco representa:** A API devolve o campo `risco_valor`. Esta é a taxa de risco climático (geralmente 20%, 30% ou 40%) caso o agricultor decida semear a lavoura *exatamente naqueles 10 dias*.

**A Transformação dos Dados (UNPIVOT):**
Ter 36 colunas diferentes no banco de dados é um pesadelo para fazer gráficos ou análises. Durante a ingestão dos dados (na Camada Gold do pipeline), aplicamos a mágica do `UNPIVOT`.
Ele pega todas essas 36 colunas que estavam "deitadas" na planilha do governo e as transforma em apenas duas colunas "em pé" na nossa API:
*   `decendio_id` (que guarda o nome, tipo "dec1", "dec15")
*   `risco_valor` (que guarda o número do risco, ex: 20, 30)

---

## 1. Monitoramento 

### `GET /api/health`
Verifica se a API está online e se a comunicação com o banco de dados PostgreSQL está ativa.

*   **Parâmetros de Busca (Query Params):** Nenhum.
*   **Resposta de Sucesso (200 OK):**
    ```json
    {
      "status": "ok",
      "database": "PostgreSQL Local na porta 5436"
    }
    ```

---

## 2. Filtros e Listagens Básicas

Rotas utilizadas para preencher caixas de seleção (dropdowns) ou autocompletar informações em interfaces (como o Streamlit ou Dashboards).

### `GET /api/filtros/ufs`
Retorna uma lista de todos os estados (UFs) únicos disponíveis no banco de dados, em ordem alfabética.
*   **Parâmetros:** Nenhum.
*   **Exemplo de Resposta (200 OK):**
    ```json
    {
      "total": 27,
      "dados": ["AC", "AL", "AM", "AP", "BA", "CE", "..."]
    }
    ```

### `GET /api/filtros/municipios`
Retorna uma lista de municípios. Se a UF for informada, retorna apenas os municípios daquele estado.
*   **Parâmetros (Query):**
    *   `uf` *(string, opcional)*: Sigla do estado para filtrar (ex: `SP`, `MG`).
*   **Exemplo de Resposta (200 OK):**
    ```json
    {
      "total": 645,
      "dados": ["ADAMANTINA", "ADOLFO", "AGUAÍ", "..."]
    }
    ```

### `GET /api/filtros/culturas`
Retorna a lista de todas as culturas agrícolas cadastradas na base.
*   **Parâmetros:** Nenhum.
*   **Exemplo de Resposta (200 OK):**
    ```json
    {
      "total": 12,
      "dados": ["ALGODÃO", "ARROZ", "FEIJÃO", "MILHO", "SOJA"]
    }
    ```

---

## 3. Consultas e Extração de Dados

### `GET /api/zarc`
Endpoint principal para busca dos dados transformados do Zarc. Permite o cruzamento de diversos filtros simultâneos.

*   **Parâmetros (Query):**
    *   `uf` *(string, opcional)*: Estado (ex: SP).
    *   `municipio` *(string, opcional)*: Nome do município.
    *   `cultura` *(string, opcional)*: Nome da cultura agrícola.
    *   `cod_solo` *(int, opcional)*: Código do tipo de solo (1, 2 ou 3).
    *   `geocodigo` *(string, opcional)*: Código IBGE do município (7 dígitos).
    *   `ano_referencia` *(int, opcional)*: Ano de referência da safra (ex: 2023).
    *   `limite` *(int, opcional)*: Quantidade máxima de registros retornados. Padrão: `500`.

*   **Regra de Negócio:** Pelo menos UM dos parâmetros textuais (`uf`, `municipio`, `cultura` ou `geocodigo`) deve ser fornecido para evitar o travamento do banco com uma busca muito ampla.

*   **Erro Comum (400 Bad Request):**
    ```json
    { "detail": "Informe ao menos um filtro" }
    ```

*   **Exemplo de Resposta (200 OK):**
    ```json
    {
      "total": 2,
      "dados": [
        {
          "uf": "SP",
          "municipio": "CAMPINAS",
          "cultura": "MILHO",
          "safra_label": "Safra 2023/2024",
          "ano_referencia": 2023,
          "cod_solo": 3,
          "geocodigo": 3509502,
          "decendio_id": "dec1",
          "risco_valor": 20.0
        },
        {
          "uf": "SP",
          "municipio": "CAMPINAS",
          "cultura": "MILHO",
          "safra_label": "Safra 2023/2024",
          "ano_referencia": 2023,
          "cod_solo": 3,
          "geocodigo": 3509502,
          "decendio_id": "dec2",
          "risco_valor": 30.0
        }
      ]
    }
    
```

---

## 4. Análise e Alertas

### `GET /api/alerta`
Fornece uma avaliação de risco rápida baseada no índice de risco climático do Zarc para um município e ano específicos.

*   **Parâmetros (Query):**
    *   `geocodigo` *(string, **obrigatório**)*: Código IBGE do município (7 dígitos).
    *   `ano_referencia` *(int, **obrigatório**)*: Ano da análise (ex: 2023).
    *   `cod_solo` *(int, opcional)*: Tipo de solo (1, 2 ou 3). Padrão: `3`.

*   **Regra de Negócio:** No padrão ZARC, os riscos toleráveis são definidos nas faixas de 20%, 30% e 40%. Se o `risco_valor` for **menor ou igual a 40%**, a API retorna um status de "Risco Aceitável". Acima disso, retorna "Atenção: Alto Risco Climático".

*   **Exemplo de Resposta (200 OK):**
    ```json
    {
      "municipio_cod": "3509502",
      "cultura": "SOJA",
      "ano_referencia": 2023,
      "risco_percentual": 30.0,
      "status_historico": "Risco Aceitável"
    }
    ```
*   **Exemplo de Resposta quando o dado não existe (200 OK):**
    ```json
    {
      "status": "Dados não encontrados no banco."
    }
    ```

---

### 💡 Dica de Uso Automático (Swagger)
Lembre-se que você não precisa montar as requisições manualmente. Com a FastAPI rodando (`uvicorn api:app --reload`), basta acessar **`http://localhost:8000/docs`** no seu navegador para testar visualmente cada um destes endpoints.
```