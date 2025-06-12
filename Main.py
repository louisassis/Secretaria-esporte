from fastapi import FastAPI, UploadFile, File # criação da API, upload de CSV e definição das rotas.
from fastapi.responses import FileResponse # Mesmo do que o de cima 
from pydantic import BaseModel # nesse aqui na classe Evento valida os campos recebidos na criação de eventos (POST /eventos).
from pymongo import MongoClient # Nessa biblioteca conecta ao MongoDB local e insere, busca ou exporta os dados dos eventos.

# O resto é intuitivo, vcs sabem o que cada uma delas fazem 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import uuid
import os
import csv
from io import StringIO

# Nas Bibliotecas, lembrar de fazer a configuração (instalação) de cada biblioteca
#Comando da Instalação
# pip install fastapi uvicorn pymongo pandas seaborn matplotlib python-multipart
# py -m uvicorn main:app --reload --port 8080
 #http://127.0.0.1:8080/docs#/default/cadastrar_evento_eventos_post

app = FastAPI()

client = MongoClient("mongodb+srv://luis:senha@cluster0.0ohfzwd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client.eventosDF

class Evento(BaseModel):
    nome: str
    data: str
    local: str
    tipo: str
    publico_estimado: int
    custo: float
    descricao: str
    regiao: str
# Esse aqui cadastra eventos

@app.post("/eventos")
def cadastrar_evento(evento: Evento):
    db.eventos.insert_one(evento.dict())
    return { " > Evento inserido com sucesso"}

# Para listar cada evento
@app.get("/eventos")
def listar_eventos():
    eventos = list(db.eventos.find({}, {"_id": 0}))
    return eventos

# Baixar o csv
@app.post("/eventos/upload-csv")
async def baixar_csv(pasta: UploadFile = File(...)):
    content = await pasta.read()
    df = pd.read_csv(StringIO(content.decode("utf-8")))

    eventos = df.to_dict(orient="records")
    db.eventos.insert_many(eventos)
    return { f"{len(eventos)} eventos inseridos com sucesso"}

# Exportar para csv, esse é para ser feito no final 
@app.get("/eventos/exportar-csv")
def exportar_csv():
    eventos = list(db.eventos.find({}, {"_id": 0}))
    if not eventos:
        return {"erro : Não tem eventos "}

    df = pd.DataFrame(eventos)
    nome_pasta = f"eventos_{uuid.uuid4()}.csv"
    df.to_csv(nome_pasta, index=False)
    return FileResponse(nome_pasta, media_type="text/csv", filename=nome_pasta)

# Primeira geração de gráficos, pensando como teste 
def gerar_grafico(df: pd.DataFrame, titulo: str, x: str, y: str, tipo='bar', agregador='sum'):
    if df.empty:
        return None

    plt.figure(figsize=(10, 6))

    if tipo == 'bar':
        sns.barplot(x=x, y=y, data=df, estimator=getattr(pd.Series, agregador), ci=None)
    elif tipo == 'count':
        sns.countplot(x=x, data=df)

    plt.title(titulo)
    plt.xticks(rotation=45)
    plt.tight_layout()

    filename = f"{uuid.uuid4()}.png"
    path = f"./{filename}"
    plt.savefig(path)
    plt.close()
    return path

#####################
# Análise dos dados #
#################3###

# Fazer uma análise do custo total por cada tipo de eventos 
# Assim vamos verificar os custos de cada tipo de evento e checar a faixa montaria 
# Tambem temos a análise de dados como eventos por região e tambem publico medio de cada um tipo de evento

@app.get("/graficos/custo-por-tipo")
def grafico_custo_por_tipo():
    eventos = list(db.eventos.find({}, {"_id": 0}))
    df = pd.DataFrame(eventos)
    pasta = gerar_grafico(df, "Custo Total por Categoria de cada Evento", "tipo", "custo", tipo="bar", agregador="sum")
    if not pasta:
        return {"Sem dados para gerar gráfico"}
    return FileResponse(pasta, media_type="image/png", filename=os.path.basename(pasta))


@app.get("/graficos/eventos-por-regiao")
def grafico_eventos_por_regiao():
    eventos = list(db.eventos.find({}, {"_id": 0}))
    df = pd.DataFrame(eventos)
    pasta = gerar_grafico(df, "Quantidade de Eventos por cada região de bsb", "regiao", "nome", tipo="count")
    if not pasta:
        return {"Sem dados para gerar gráfico"}
    return FileResponse(pasta, media_type="image/png", filename=os.path.basename(pasta))


@app.get("/graficos/publico-medio-por-tipo")
def grafico_publico_medio_por_tipo():
    eventos = list(db.eventos.find({}, {"_id": 0}))
    df = pd.DataFrame(eventos)
    pasta = gerar_grafico(df, "Público Médio por Categória de cada evento", "tipo", "publico_estimado", tipo="bar", agregador="mean")
    if not pasta:
        return {"Sem dados para gerar gráfico"}
    return FileResponse(pasta, media_type="image/png", filename=os.path.basename(pasta))
