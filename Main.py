from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pymongo import MongoClient
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

app = FastAPI()
client = MongoClient("mongodb://localhost:27017")
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
def add_evento(evento: Evento):
    db.eventos.insert_one(evento.dict())
    return {"message": "Evento inserido com sucesso"}

# Para listar cada evento
@app.get("/eventos")
def listar_eventos():
    eventos = list(db.eventos.find({}, {"_id": 0}))
    return eventos

# Baixar o csv
@app.post("/eventos/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    content = await file.read()
    df = pd.read_csv(StringIO(content.decode("utf-8")))

    eventos = df.to_dict(orient="records")
    db.eventos.insert_many(eventos)
    return {"message": f"{len(eventos)} eventos inseridos com sucesso"}

# Exportar para csv, esse é para ser feito no final 
@app.get("/eventos/exportar-csv")
def exportar_csv():
    eventos = list(db.eventos.find({}, {"_id": 0}))
    if not eventos:
        return {"erro": "Sem eventos para exportar"}

    df = pd.DataFrame(eventos)
    filename = f"eventos_{uuid.uuid4()}.csv"
    df.to_csv(filename, index=False)
    return FileResponse(filename, media_type="text/csv", filename=filename)

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
    path = gerar_grafico(df, "Custo Total por Tipo de Evento", "tipo", "custo", tipo="bar", agregador="sum")
    if not path:
        return {"erro": "Sem dados para gerar gráfico"}
    return FileResponse(path, media_type="image/png", filename=os.path.basename(path))


@app.get("/graficos/eventos-por-regiao")
def grafico_eventos_por_regiao():
    eventos = list(db.eventos.find({}, {"_id": 0}))
    df = pd.DataFrame(eventos)
    path = gerar_grafico(df, "Quantidade de Eventos por Região", "regiao", "nome", tipo="count")
    if not path:
        return {"erro": "Sem dados para gerar gráfico"}
    return FileResponse(path, media_type="image/png", filename=os.path.basename(path))


@app.get("/graficos/publico-medio-por-tipo")
def grafico_publico_medio_por_tipo():
    eventos = list(db.eventos.find({}, {"_id": 0}))
    df = pd.DataFrame(eventos)
    path = gerar_grafico(df, "Público Médio por Tipo de Evento", "tipo", "publico_estimado", tipo="bar", agregador="mean")
    if not path:
        return {"erro": "Sem dados para gerar gráfico"}
    return FileResponse(path, media_type="image/png", filename=os.path.basename(path))
