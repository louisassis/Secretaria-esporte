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

# Conexão com MongoDB
client = MongoClient(
    "mongodb+srv://luis:senha@cluster0.0ohfzwd.mongodb.net/eventosDF"
    "?retryWrites=true&w=majority&appName=Cluster0"
)
db = client.eventosDF

# Modelo de evento
class Evento(BaseModel):
    nome: str
    data: str
    local: str
    tipo: str
    publico_estimado: int
    custo: float
    descricao: str
    regiao: str

# -------------------- CRUD DE EVENTOS --------------------

@app.post("/eventos")
def cadastrar_evento(evento: Evento):
    """Cadastra um evento no MongoDB."""
    db.eventos.insert_one(evento.dict())
    return {"message": "Evento inserido com sucesso"}

@app.get("/eventos")
def listar_eventos():
    """Lista todos os eventos."""
    eventos = list(db.eventos.find({}, {"_id": 0}))
    return eventos

@app.post("/eventos/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Recebe CSV de eventos e insere no MongoDB."""
    content = await file.read()
    df = pd.read_csv(StringIO(content.decode("utf-8")))
    registros = df.to_dict(orient="records")
    db.eventos.insert_many(registros)
    return {"message": f"{len(registros)} eventos inseridos com sucesso"}

@app.get("/eventos/exportar-csv")
def exportar_csv():
    """Exporta todos os eventos para CSV e retorna download."""
    eventos = list(db.eventos.find({}, {"_id": 0}))
    if not eventos:
        return {"error": "Não há eventos para exportar"}
    df = pd.DataFrame(eventos)
    filename = f"eventos_{uuid.uuid4()}.csv"
    df.to_csv(filename, index=False)
    return FileResponse(filename, media_type="text/csv", filename=filename)

# -------------------- GRÁFICOS A PARTIR DE CSV --------------------

CSV_PATH = "eventos.csv"

@app.get("/graficos/eventos-2semestre-2025")
def grafico_eventos_2semestre_2025():
    """Número de eventos por mês no 2º semestre de 2025."""
    df = pd.read_csv(CSV_PATH, parse_dates=["data"])
    df2025 = df[df["data"].dt.year == 2025]
    contagens = (
        df2025["data"]
            .dt.month
            .value_counts()
            .reindex(range(7, 13), fill_value=0)
    )
    meses = ["Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    colors = sns.color_palette("mako", len(meses))

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(range(len(meses)), contagens.values, color=colors, edgecolor="gray", width=0.6)
    ax.set_xticks(range(len(meses)))
    ax.set_xticklabels(meses, fontsize=12)
    ax.set_title("Número de Eventos por Mês (2º Semestre - 2025)",
                 fontsize=20, fontfamily="serif", fontstyle="italic", pad=20)
    ax.set_xlabel("Meses", fontsize=14, fontweight="bold")
    ax.set_ylabel("Quantidade de Eventos", fontsize=14, fontweight="bold")
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    fname = f"{uuid.uuid4()}.png"
    plt.tight_layout()
    fig.savefig(fname)
    plt.close(fig)
    return FileResponse(fname, media_type="image/png", filename=os.path.basename(fname))

@app.get("/graficos/distribuicao-eventos-por-regiao")
def grafico_distribuicao_eventos_por_regiao():
    """Distribuição de eventos por região, agrupando pequenas em 'Outros'."""
    df = pd.read_csv(CSV_PATH)
    counts = df["regiao"].value_counts()
    threshold = counts.sum() * 0.05
    small = counts[counts < threshold]
    big = counts[counts >= threshold].copy()
    big["Outros"] = small.sum()
    big = big.sort_values(ascending=False)

    colors = ["#FF0000", "#00FFFF", "#90EE90", "#D8BFD8",
              "#FFFF00", "#FFD580", "#F5F5DC", "#A9A9A9"]
    pie_colors = colors[: len(big)]

    fig, ax = plt.subplots(figsize=(18, 10))
    ax.pie(big.values, labels=big.index, colors=pie_colors,
           autopct="%1.0f%%", startangle=90,
           wedgeprops={"edgecolor": "black", "linewidth": 1.5},
           textprops={"fontsize": 14, "fontweight": "bold", "color": "black"},
           labeldistance=1.1)
    fig.suptitle("Distribuição de Eventos por Região",
                 fontsize=24, fontfamily="serif", fontweight="bold", y=0.98)

    handles = [Patch(facecolor="none", edgecolor="none") for _ in small.index]
    fig.legend(handles, list(small.index), title="Outros:",
               loc="center right", bbox_to_anchor=(1, 0.5),
               fontsize=12, title_fontsize=14,
               frameon=True, edgecolor="black", fancybox=False)

    fname = f"{uuid.uuid4()}.png"
    plt.tight_layout()
    fig.savefig(fname)
    plt.close(fig)
    return FileResponse(fname, media_type="image/png", filename=os.path.basename(fname))

@app.get("/graficos/top10-investimento")
def grafico_top10_investimento():
    """Top 10 esportes com maior investimento médio."""
    df = pd.read_csv(CSV_PATH)
    grouped = df.groupby("tipo")["custo"].agg(["sum", "count"])
    grouped["avg_cost"] = grouped["sum"] / grouped["count"]
    top10 = grouped["avg_cost"].sort_values(ascending=False).head(10)

    colors = sns.color_palette("mako", len(top10))
    x = np.arange(len(top10)) * 1.8

    fig, ax = plt.subplots(figsize=(16, 7))
    ax.bar(x, top10.values, width=1.2, color=colors, edgecolor="gray")
    max_val = top10.max()
    for xi, h in zip(x, top10.values):
        ax.text(xi, h + max_val * 0.01, f"R$ {h:,.0f}".replace(",", "."),
                ha="center", va="bottom", fontsize=12, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(top10.index, rotation=0, fontsize=12)
    ax.set_title("Esportes com Maior Investimento no DF",
                 fontsize=20, fontfamily="serif", fontstyle="italic", pad=25)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(left=False, bottom=False)
    ax.get_yaxis().set_visible(False)

    fname = f"{uuid.uuid4()}.png"
    plt.tight_layout()
    fig.savefig(fname)
    plt.close(fig)
    return FileResponse(fname, media_type="image/png", filename=os.path.basename(fname))

@app.get("/graficos/top10-publico")
def grafico_top10_publico():
    """Top 10 esportes com maior público total."""
    df = pd.read_csv(CSV_PATH)
    total_audience = df.groupby("tipo")["publico_estimado"].sum().sort_values(ascending=False).head(10)

    colors = sns.color_palette("inferno", len(total_audience))
    fig, ax = plt.subplots(figsize=(16, 7))
    bars = ax.bar(total_audience.index, total_audience.values, color=colors, edgecolor="gray")
    max_val = total_audience.max()
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + max_val * 0.01,
                f"{int(h):,}".replace(",", "."), ha="center", va="bottom",
                fontsize=12, fontweight="bold")

    ax.set_title("Esportes com Maior Público em Brasília",
                 fontsize=20, fontfamily="serif", fontstyle="italic", pad=20)
    ax.set_xlabel("Esporte", fontsize=14, fontweight="bold")
    ax.set_ylabel("Público Total", fontsize=14, fontweight="bold")
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    fname = f"{uuid.uuid4()}.png"
    plt.tight_layout()
    fig.savefig(fname)
    plt.close(fig)
    return FileResponse(fname, media_type="image/png", filename=os.path.basename(fname))