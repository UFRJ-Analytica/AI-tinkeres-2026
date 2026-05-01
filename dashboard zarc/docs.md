Aqui está a documentação oficial, estruturada e detalhada para todas as rotas `GET` da sua nova API. 

Você pode guardar este documento como o seu **"Contrato de API"** (ou arquivo `README.md` do projeto) para saber exatamente como consumir os dados.

---

# 📖 Documentação da API: SafraViva (Zarc - PostgreSQL)

Esta API fornece acesso rápido e parametrizado aos dados do Zoneamento Agrícola de Risco Climático (Zarc) armazenados no banco de dados PostgreSQL.

*   **Base URL (Local):** `http://localhost:8000`
*   **Formato de Resposta:** `application/json`
*   **Interface Interativa (Swagger):** Disponível em `http://localhost:8000/docs`

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

Rotas utilizadas para preencher caixas de seleção (dropdowns) ou autocompletar informações em interfaces (como o Streamlit).

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
Endpoint principal para busca dos dados brutos do Zarc. Permite o cruzamento de diversos filtros simultâneos.

*   **Parâmetros (Query):**
    *   `uf` *(string, opcional)*: Estado (ex: SP).
    *   `municipio` *(string, opcional)*: Nome do município.
    *   `cultura` *(string, opcional)*: Nome da cultura agrícola.
    *   `cod_solo` *(int, opcional)*: Código do tipo de solo (ex: 1, 2 ou 3).
    *   `geocodigo` *(string, opcional)*: Código IBGE do município (7 dígitos).
    *   `safra_ini` *(int, opcional)*: Ano de início da safra (ex: 2023).
    *   `limite` *(int, opcional)*: Quantidade máxima de registros retornados. Padrão: `500`.

*   **Regra de Negócio:** Pelo menos UM dos parâmetros textuais (`uf`, `municipio`, `cultura` ou `geocodigo`) deve ser fornecido para evitar o travamento do banco com uma busca inteira acidental.

*   **Erro Comum (400 Bad Request):**
    ```json
    { "detail": "Informe ao menos um filtro" }
    ```

*   **Exemplo de Resposta (200 OK):**
    ```json
    {
      "total": 1,
      "dados": [
        {
          "UF": "SP",
          "municipio": "CAMPINAS",
          "geocodigo": "3509502",
          "Nome_cultura": "MILHO",
          "Cod_Solo": 3,
          "SafraIni": 2023,
          "valor_frequencia": 85.5
        }
      ]
    }
    ```

---

## 4. Análise e Alertas

### `GET /api/alerta`
Fornece uma avaliação de risco rápida baseada na frequência histórica de sucesso da cultura para um município e ano específicos.

*   **Parâmetros (Query):**
    *   `geocodigo` *(string, **obrigatório**)*: Código IBGE do município (7 dígitos).
    *   `ano` *(int, **obrigatório**)*: Ano da análise (ex: 2023).
    *   `solo` *(int, opcional)*: Tipo de solo (1, 2 ou 3). Padrão: `3`.

*   **Regra de Negócio:** Se a frequência de sucesso (`valor_frequencia`) for menor que 80%, a API retorna um status de "Alto Risco Climático". Caso contrário, retorna "Risco Aceitável".

*   **Exemplo de Resposta (200 OK):**
    ```json
    {
      "municipio_cod": "3509502",
      "cultura": "SOJA",
      "ano": 2023,
      "frequencia_sucesso": 65.0,
      "status_historico": "Atenção: Alto Risco Climático"
    }
    ```
*   **Exemplo de Resposta quando o dado não existe (200 OK):**
    ```json
    {
      "status": "Dados não encontrados no banco."
    }
    ```

---

### 💡 Dica Bônus sobre o FastAPI
Você não precisa construir essa documentação manualmente no futuro! O FastAPI faz isso sozinho. Com a sua API rodando no terminal, abra o navegador e acesse **`http://localhost:8000/docs`**. 

Você verá uma página interativa gerada automaticamente (Swagger) onde pode não apenas ler a documentação, mas também testar as rotas clicando em "Try it out" sem precisar escrever uma única linha de código.
```