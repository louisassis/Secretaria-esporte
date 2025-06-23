from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pymongo import MongoClient
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import uuid
import os
from io import StringIO
from matplotlib.patches import Patch

app = FastAPI()

# #--------------------------------------------------
#  CONFIGURAÇÃO DO BANCO DE DADOS (MongoDB Atlas)
# --------------------------------------------------

cliente = MongoClient(
    "mongodb+srv://luis:senha@cluster0.0ohfzwd.mongodb.net/eventosDF"
    "?retryWrites=true&w=majority&appName=Cluster0"
)
# Seleciona o banco de dados 'eventosDF'

db = cliente.eventosDF

# --------------------------------------------------
#  MODELO DE DADOS DO EVENTO
# --------------------------------------------------

class Evento(BaseModel):
    nome: str
    data: str
    local: str
    tipo: str
    publico_estimado: int
    custo: float
    descricao: str
    regiao: str

# --------------------------------------------------
#  ROTAS DE CRUD DE EVENTOS
# --------------------------------------------------

#Cadastra um evento no MongoDB. Recebe um JSON com os campos definidos em Evento.
@app.post("/eventos")
def cadastrar_evento(novo_evento: Evento):

    db.eventos.insert_one(novo_evento.dict())
    return {"message": "Evento inserido com sucesso"}

# Lista todos os eventos cadastrados no MongoDB.Retorna uma lista de dicionários sem o campo '_id'.
@app.get("/eventos")
def listar_eventos():

    lista_eventos = list(db.eventos.find({}, {"_id": 0}))
    return lista_eventos


# Faz upload de um arquivo CSV com eventos. Lê o conteúdo, converte para DataFrame e insere todos os registros.
@app.post("/eventos/upload-csv")
async def enviar_csv(arquivo: UploadFile = File(...)):

    conteudo = await arquivo.read()
    dados = pd.read_csv(StringIO(conteudo.decode("utf-8")))
    lista_registros = dados.to_dict(orient="records")
    db.eventos.insert_many(lista_registros)
    return {"message": f"{len(lista_registros)} eventos inseridos com sucesso"}


#  Exporta todos os eventos para um arquivo CSV e permite download.
@app.get("/eventos/exportar-csv")
def exportar_csv():

    lista_eventos = list(db.eventos.find({}, {"_id": 0}))
    if not lista_eventos:
        return {"error": "Não há eventos para exportar"}

    df_export = pd.DataFrame(lista_eventos)
    nome_arquivo_csv = f"eventos_{uuid.uuid4()}.csv"
    df_export.to_csv(nome_arquivo_csv, index=False)
    return FileResponse(nome_arquivo_csv,
                        media_type="text/csv",
                        filename=nome_arquivo_csv)



# -------------------------------
#  GRÁFICOS A PARTIR DO CSV
# -------------------------------


CSV_CAMINHO = "eventos.csv"

@app.get("/graficos/eventos-2semestre-2025")
def grafico_2semestre_2025():
    df = pd.read_csv(CSV_CAMINHO, parse_dates=["data"])
    dados2025 = df[df["data"].dt.year == 2025]
    contagem_mensal = (
        dados2025["data"]
        .dt.month
        .value_counts()
        .reindex(range(7, 13), fill_value=0)
    )

    lista_meses = ["Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    paleta_cores = sns.color_palette("mako", len(lista_meses))

    figura, ax = plt.subplots(figsize=(12,6))
    ax.bar(range(len(lista_meses)),
             contagem_mensal.values,
             color=paleta_cores,
             edgecolor="gray",
             width=0.6)

    ax.set_xticks(range(len(lista_meses)))
    ax.set_xticklabels(lista_meses, fontsize=12)
    ax.set_title("Eventos por Mês (2º Semestre 2025)",
                   fontsize=18, fontweight="bold")
    ax.set_xlabel("Mês", fontsize=14)
    ax.set_ylabel("Número de Eventos", fontsize=14)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    plt.tight_layout()
    nome_imagem = f"{uuid.uuid4()}.png"
    figura.savefig(nome_imagem)
    plt.close(figura)

    return FileResponse(nome_imagem,
                        media_type="image/png",
                        filename=os.path.basename(nome_imagem))

@app.get("/graficos/distribuicao-eventos-por-regiao")
def grafico_eventos_por_regiao():

    df = pd.read_csv(CSV_CAMINHO)
    contagens = df["regiao"].value_counts()
    limiar = contagens.sum() * 0.05
    regs_pequenas = contagens[contagens < limiar]
    regs_grandes = contagens[contagens >= limiar].copy()
    regs_grandes["Outros"] = regs_pequenas.sum()
    regs_ordenadas = regs_grandes.sort_values(ascending=False)

    cores_pizza = ["#FF0000","#00FFFF","#90EE90","#D8BFD8",
                   "#FFFF00","#FFD580","#F5F5DC","#A9A9A9"]
    fatias = cores_pizza[:len(regs_ordenadas)]

    figura, ax = plt.subplots(figsize=(14,10))
    ax.pie(regs_ordenadas.values,
            labels=regs_ordenadas.index,
            colors=fatias,
            autopct="%1.0f%%",
            startangle=90,
            wedgeprops={"edgecolor":"black","linewidth":1.5},
            textprops={"fontsize":12,"fontweight":"bold"})
    figura.suptitle("Distribuição de Eventos por Região",
                    fontsize=20, fontweight="bold", y=0.95)

    leg_handles = [Patch(facecolor="none", edgecolor="none")
                   for _ in regs_pequenas.index]
    figura.legend(leg_handles,
                  list(regs_pequenas.index),
                  title="Outros",
                  loc="center right",
                  bbox_to_anchor=(1,0.5))

    plt.tight_layout()
    nome_imagem = f"{uuid.uuid4()}.png"
    figura.savefig(nome_imagem)
    plt.close(figura)

    return FileResponse(nome_imagem,
                        media_type="image/png",
                        filename=os.path.basename(nome_imagem))

@app.get("/graficos/top10-investimento")
def grafico_top10_investimento():

    df = pd.read_csv(CSV_CAMINHO)
    agrupado = df.groupby("tipo")["custo"].agg(["sum","count"])
    agrupado["media"] = agrupado["sum"] / agrupado["count"]
    top10 = agrupado["media"].sort_values(ascending=False).head(10)

    paleta = sns.color_palette("mako", len(top10))
    posicoes = np.arange(len(top10)) * 1.8

    figura, ax = plt.subplots(figsize=(16,7))
    ax.bar(posicoes, top10.values,
             color=paleta, edgecolor="gray", width=1.2)
    valor_max = top10.max()
    for x_pos, altura in zip(posicoes, top10.values):
        ax.text(x_pos, altura + valor_max*0.01,
                  f"R$ {altura:,.0f}".replace(",","."),
                  ha="center", va="bottom")

    ax.set_xticks(posicoes)
    ax.set_xticklabels(top10.index, fontsize=12)
    ax.set_title("Top 10 Investimento Médio por Esporte",
                   fontsize=18, fontweight="bold")
    ax.yaxis.set_visible(False)
    plt.tight_layout()

    nome_imagem = f"{uuid.uuid4()}.png"
    figura.savefig(nome_imagem)
    plt.close(figura)

    return FileResponse(nome_imagem,
                        media_type="image/png",
                        filename=os.path.basename(nome_imagem))

@app.get("/graficos/top10-publico")
def grafico_top10_publico():

    df = pd.read_csv(CSV_CAMINHO)
    publico_total = df.groupby("tipo")["publico_estimado"].sum()
    top10 = publico_total.sort_values(ascending=False).head(10)

    paleta = sns.color_palette("inferno", len(top10))
    figura, ax = plt.subplots(figsize=(16,7))
    barras = ax.bar(top10.index, top10.values,
                      color=paleta, edgecolor="gray")
    valor_max = top10.max()
    for barra in barras:
        altura = barra.get_height()
        ax.text(barra.get_x()+barra.get_width()/2,
                  altura + valor_max*0.01,
                  f"{int(altura):,}".replace(",","."),
                  ha="center", va="bottom")

    ax.set_title("Esportes com Maior Público Total",
                   fontsize=18, fontweight="bold")
    ax.set_xlabel("Esporte")
    ax.set_ylabel("Público Total")
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    nome_imagem = f"{uuid.uuid4()}.png"
    figura.savefig(nome_imagem)
    plt.close(figura)

    return FileResponse(nome_imagem,
                        media_type="image/png",
                        filename=os.path.basename(nome_imagem))
