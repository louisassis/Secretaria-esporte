
# 📊 Plataforma de Gestão e Análise de Eventos (FastAPI + MongoDB)

Este projeto é uma API desenvolvida com **FastAPI** e conectada ao **MongoDB Atlas**. A plataforma permite:

- Cadastrar eventos manualmente ou via upload de CSV
- Listar e exportar eventos para CSV
- Gerar gráficos analíticos (custo por tipo, eventos por região, público médio por categoria)

---

## 🚀 Como rodar o projeto

### 1. Clone o repositório (se aplicável)

```bash
git clone https://github.com/seu-usuario/seu-projeto.git
cd seu-projeto
```

### 2. Crie um ambiente virtual (opcional, mas recomendado)

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install fastapi uvicorn pymongo pandas seaborn matplotlib python-multipart
```

---

## ⚙️ Executar o servidor

```bash
uvicorn nome_do_arquivo:app --reload
```

> Substitua `nome_do_arquivo` pelo nome real do seu script, por exemplo: `main`.

A API estará disponível em: `http://127.0.0.1:8000`

Você pode testar os endpoints interativamente em: `http://127.0.0.1:8000/docs`

---

## ☁️ Conexão com MongoDB Atlas

A conexão está definida da seguinte forma:

```python
client = MongoClient("mongodb+srv://USUARIO:SENHA@cluster.mongodb.net/eventosDF")
```

> Lembre-se de substituir `USUARIO` e `SENHA` pelas credenciais reais. Você pode armazená-las com segurança usando variáveis de ambiente e a biblioteca `python-dotenv` para evitar expor senhas diretamente no código.

---

## 📌 Principais Endpoints

### ➕ Cadastrar evento manualmente

`POST /eventos`

```json
{
  "nome": "Evento X",
  "data": "2024-05-20",
  "local": "Parque da Cidade",
  "tipo": "Cultural",
  "publico_estimado": 500,
  "custo": 12000.50,
  "descricao": "Descrição do evento",
  "regiao": "Plano Piloto"
}
```

---

### 📋 Listar todos os eventos

`GET /eventos`

---

### ⬆️ Upload de CSV com eventos

`POST /eventos/upload-csv`

- Enviar arquivo `.csv` com colunas correspondentes aos campos dos eventos.

---

### ⬇️ Exportar eventos para CSV

`GET /eventos/exportar-csv`

---

## 📊 Gráficos Analíticos

### 💰 Custo total por tipo de evento

`GET /graficos/custo-por-tipo`

### 🗺️ Quantidade de eventos por região

`GET /graficos/eventos-por-regiao`

### 👥 Público médio por tipo de evento

`GET /graficos/publico-medio-por-tipo`

---

## 🧼 Estrutura de Arquivo CSV esperada

| nome | data | local | tipo | publico_estimado | custo | descricao | regiao |
|------|------|-------|------|------------------|-------|-----------|--------|
| Festa Junina | 2024-06-23 | Ceilândia | Cultural | 1500 | 8000 | Festa com quadrilha e comidas típicas | Ceilândia |

---

## 📎 Notas Finais

- Os gráficos são salvos como arquivos `.png` e retornados como resposta da API.
- A conexão com o MongoDB deve ser protegida usando `.env` em produção.
- Lembre-se de configurar permissões no Atlas para permitir conexões externas ao cluster.

