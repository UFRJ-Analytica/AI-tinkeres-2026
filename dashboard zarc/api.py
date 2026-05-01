from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
import pandas as pd
import os

# ==============================
# CONFIGURAÇÕES DO BANCO (DOCKER)
# ==============================
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5436") # A porta externa que configuramos
DB_NAME = os.getenv("DB_NAME", "mydatabase")
DB_USER = os.getenv("DB_USER", "myuser")
DB_PASS = os.getenv("DB_PASS", "mypassword")
TABLE_NAME = "public.dados_safra_front"

# ==============================
# INICIALIZANDO A API
# ==============================
app = FastAPI(title="API Zarc (PostgreSQL)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão com o banco: {str(e)}")

# ==============================
# ENDPOINTS (ROTAS)
# ==============================
@app.get("/api/health")
def health():
    return {"status": "ok", "database": "PostgreSQL Local na porta 5436"}

@app.get("/api/filtros/ufs")
def listar_ufs():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(f'SELECT DISTINCT UPPER(TRIM("UF")) AS uf FROM {TABLE_NAME} WHERE "UF" IS NOT NULL ORDER BY uf')
    rows = cursor.fetchall()
    conn.close()
    return {"total": len(rows), "dados": [r["uf"] for r in rows]}

@app.get("/api/filtros/municipios")
def listar_municipios(uf: Optional[str] = None):
    query = f'SELECT DISTINCT UPPER(TRIM("municipio")) AS municipio FROM {TABLE_NAME} WHERE "municipio" IS NOT NULL'
    params = []
    if uf:
        query += ' AND UPPER(TRIM("UF")) = %s'
        params.append(uf.upper().strip())
    query += " ORDER BY municipio"

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return {"total": len(rows), "dados": [r["municipio"] for r in rows]}

@app.get("/api/filtros/culturas")
def listar_culturas():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(f'SELECT DISTINCT UPPER(TRIM("Nome_cultura")) AS cultura FROM {TABLE_NAME} WHERE "Nome_cultura" IS NOT NULL ORDER BY cultura')
    rows = cursor.fetchall()
    conn.close()
    return {"total": len(rows), "dados": [r["cultura"] for r in rows]}

@app.get("/api/zarc")
def zarc(
    uf: Optional[str] = None,
    municipio: Optional[str] = None,
    cultura: Optional[str] = None,
    cod_solo: Optional[int] = None,
    geocodigo: Optional[str] = None,
    safra_ini: Optional[int] = None,
    limite: int = 500
):
    if not any([uf, municipio, cultura, geocodigo]):
        raise HTTPException(status_code=400, detail="Informe ao menos um filtro")

    query = f'SELECT * FROM {TABLE_NAME} WHERE 1=1'
    params = []

    if uf:
        query += ' AND UPPER("UF") = %s'
        params.append(uf.upper())
    if municipio:
        query += ' AND UPPER("municipio") = %s'
        params.append(municipio.upper())
    if cultura:
        query += ' AND UPPER("Nome_cultura") = %s'
        params.append(cultura.upper())
    if cod_solo:
        query += ' AND "Cod_Solo" = %s'
        params.append(cod_solo)
    if safra_ini:
        query += ' AND "SafraIni" = %s'
        params.append(safra_ini)
    if geocodigo:
        query += ' AND CAST("geocodigo" AS TEXT) = %s'
        params.append(str(geocodigo).strip())

    query += " LIMIT %s"
    params.append(limite)

    try:
        conn = get_db_connection()
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return {"total": len(df), "dados": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alerta")
def alerta(geocodigo: str = Query(...), ano: int = Query(...), solo: int = Query(3)):
    query = f'SELECT "valor_frequencia", "Nome_cultura" FROM {TABLE_NAME} WHERE CAST("geocodigo" AS TEXT) = %s AND "SafraIni" = %s AND "Cod_Solo" = %s LIMIT 1'
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(query, [str(geocodigo), int(ano), int(solo)])
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"status": "Dados não encontrados no banco."}

    freq = float(row["valor_frequencia"])
    status = "Risco Aceitável" if freq >= 80 else "Atenção: Alto Risco Climático"
    
    return {
        "municipio_cod": geocodigo,
        "cultura": row["Nome_cultura"],
        "ano": ano,
        "frequencia_sucesso": freq,
        "status_historico": status
    }