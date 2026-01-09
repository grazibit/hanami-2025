# hanami-2025

Projeto de exemplo para processar arquivos CSV/XLSX e gerar relatórios analíticos com FastAPI e pandas.

## Requisitos

- Python 3.10+
- `pip` instalado

## Instalação (Windows)

1. Instale dependências:

```powershell
pip install -r requirements.txt
```

Observação: a escrita em formato Parquet depende de um engine opcional (`pyarrow` ou `fastparquet`). Se pretende utilizar arquivos `.parquet`, instale `pyarrow`:

```powershell
pip install pyarrow
```

2. Rodar a aplicação (desenvolvimento):

```powershell
python -m uvicorn app.main:app --reload
```

> Usar `python -m uvicorn` é mais robusto quando `uvicorn` não está no PATH.

## Endpoints úteis
- Upload de arquivo: `POST /upload` (form field `file`)
- Relatórios:
  - `GET /reports/sales-summary`
  - `GET /reports/product-analysis?top_n=10&sort_by=total_arrecadado`
  - `GET /reports/financial-metrics?version=<versao>` — retorna `lucro_bruto`, `receita_liquida` e `custo_total` como números

## Exemplos

PowerShell (upload):

```powershell
curl.exe -F "file=@vendas_ficticias_10000_linhas.csv" http://127.0.0.1:8000/upload
```

curl (consulta métricas financeiras para uma versão específica):

```bash
curl "http://127.0.0.1:8000/reports/financial-metrics?version=666c0b3465d0475abaa6f79ad07420e9"
```

## Estrutura do projeto

- `app/` – código da aplicação (endpoints, parser, lógica de negócio)
- `docs/` – documentação adicional
- `exports/` – arquivos processados e relatórios (versionados). Os arquivos `.parquet` são usados pela API para carregar versões.
- `logs/` – arquivos de log (`logs/app.log`)

## Observações e boas práticas

- Os arquivos `*.csv` gerados durante o upload são cópias brutas. Você pode movê-los para `exports/archive/` ou removê-los se não precisar mais.
- Mantenha os arquivos `.parquet` se quiser que as versões continuem acessíveis via API (`GET /reports/...`).

---

## Requisitos

- Python 3.10+
- `pip` instalado

## Instalação (Windows)

1. Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instale dependências:

```powershell
pip install -r requirements.txt
```

3. Rodar a aplicação (desenvolvimento):

```powershell
uvicorn app.main:app --reload
```

4. Endpoints:

- Upload: `POST /upload` (form field `file`)

## Estrutura inicial

- `app/` – código da aplicação
- `docs/` – documentação adicional
- `exports/` – arquivos processados e relatórios (versionados)
- `logs/` – arquivos de log

## Observações

- A API usa `pandas` para leitura e validação dos arquivos.
- Logs são gravados em `logs/app.log`.
- status: em andamento.
# hanami-2025
