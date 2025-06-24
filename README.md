# Guia Passo a Passo para Obter os Gráficos

Este documento descreve como configurar e executar a aplicação para gerar e baixar os gráficos de eventos.

## Requisitos

- Python 3.8 ou superior
- MongoDB Atlas (ou local) ou arquivo CSV `eventos.csv`
- Pacotes Python:
  - fastapi
  - uvicorn
  - pymongo
  - pandas
  - seaborn
  - matplotlib
  - numpy

## Passo 1 – Obter o Código

Clone ou copie o arquivo `main1.py` para o seu diretório de trabalho.

```bash
git clone <repositório>  # se aplicável
# ou copie manualmente main1.py
```

## Passo 2 – Instalar Dependências

No terminal, dentro da pasta do projeto:

```bash
pip install fastapi uvicorn pymongo pandas seaborn matplotlib numpy
```

## Passo 3 – Configurar a Conexão com o MongoDB

Edite o arquivo `main1.py` (linha onde `MongoClient` é inicializado) e substitua `senha` e o nome do banco de dados pelos seus valores.

Opcional: use variáveis de ambiente e `python-dotenv` para manter credenciais seguras.

## Passo 4 – Iniciar a Aplicação

Execute o servidor FastAPI com `uvicorn`:

```bash
uvicorn main1:app --reload
```

O servidor ficará disponível em `http://127.0.0.1:8000`.

## Passo 5 – Preparar os Dados

### 5.1 Usar Banco de Dados

Insira eventos via endpoints:
- `POST /eventos` – cadastra um evento único (JSON).
- `POST /eventos/upload-csv` – faz upload de um CSV.

### 5.2 Usar CSV Local

Renomeie ou copie seu CSV de eventos para `eventos.csv` na raiz do projeto.

## Passo 6 – Gerar e Baixar os Gráficos

Acesse no navegador ou via `curl` os seguintes endpoints:

1. **Gráfico 1** – Eventos por Mês (2º Semestre 2025)  
   `GET http://127.0.0.1:8000/graficos/eventos-2semestre-2025`

2. **Gráfico 2** – Distribuição de Eventos por Região  
   `GET http://127.0.0.1:8000/graficos/distribuicao-eventos-por-regiao`

3. **Gráfico 3** – Top 10 Investimento Médio por Esporte  
   `GET http://127.0.0.1:8000/graficos/top10-investimento`

4. **Gráfico 4** – Esportes com Maior Público Total  
   `GET http://127.0.0.1:8000/graficos/top10-publico`

Cada endpoint retornará um arquivo PNG que pode ser salvo localmente.

