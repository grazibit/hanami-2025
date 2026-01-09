from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import uuid
import logging
from app.config import EXPORTS_DIR, LOGS_DIR
from app.utils.parser import read_file, validate_and_normalize
from app import reports
import pandas as pd
import json

app = FastAPI(title="API de Análises CSV/XLSX")

LOGS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Configurar logging: saída para console e para arquivo `app.log`
log_file = str(LOGS_DIR / "app.log")
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Adiciona FileHandler se ainda não existir (para evitar duplicação)
has_file = any(isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", None) == log_file for h in root_logger.handlers)
if not has_file:
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    root_logger.addHandler(fh)

# Adiciona StreamHandler (console) se ainda não existir
has_stream = any(isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler) for h in root_logger.handlers)
if not has_stream:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    root_logger.addHandler(ch)


def _latest_version_parquet() -> Path | None:
    files = list(EXPORTS_DIR.glob("*.parquet"))
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def _load_df_for_version(version: str | None) -> pd.DataFrame:
    if version:
        path = EXPORTS_DIR / f"{version}.parquet"
        if not path.exists():
            raise HTTPException(status_code=404, detail="Versão não encontrada")
        return pd.read_parquet(path)
    latest = _latest_version_parquet()
    if not latest:
        raise HTTPException(status_code=404, detail="Nenhum dado disponível")
    return pd.read_parquet(latest)


# In-memory store for processed DataFrames: version_id -> DataFrame
processed_store: dict[str, pd.DataFrame] = {}


@app.post("/upload")
async def upload(file: UploadFile = File(None)):
    if not file or not getattr(file, "filename", None):
        return JSONResponse(status_code=400, content={"erro": "Nenhum arquivo enviado"})

    suffix = Path(file.filename).suffix.lower()
    if suffix not in (".csv", ".xls", ".xlsx"):
        return JSONResponse(status_code=400, content={"erro": "Tipo de arquivo não suportado"})

    version_id = uuid.uuid4().hex
    dest = EXPORTS_DIR / f"{version_id}{suffix}"

    with dest.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    logging.info(f"Arquivo enviado: {file.filename} -> {dest}")

    # process
    try:
        df = read_file(dest)
        df, errors = validate_and_normalize(df)
        if errors:
            logging.warning(f"Avisos de validação: {errors}")

        # save processed dataframe for versioned analysis (in-memory and on-disk)
        processed_store[version_id] = df
        parquet_path = EXPORTS_DIR / f"{version_id}.parquet"
        df.to_parquet(parquet_path, index=False)

        # generate summary report
        report = reports.sales_summary(df)
        report.update({"versao": version_id})

        report_path = EXPORTS_DIR / f"report_{version_id}.json"
        with report_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logging.info(f"Relatório salvo: {report_path}")

        linhas_processadas = len(df)
        return JSONResponse(status_code=200, content={"status": "sucesso", "linhas_processadas": linhas_processadas, "versao": version_id})

    except ValueError as e:
        logging.error("Validação falhou: %s", str(e))
        return JSONResponse(status_code=422, content={"erros": [str(e)]})
    except Exception as e:
        logging.exception("Processamento falhou")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports/sales-summary")
def get_sales_summary(version: str | None = Query(None)):
    df = _load_df_for_version(version)
    return reports.sales_summary(df)


@app.get("/reports/regional-performance")
def get_regional_performance(version: str | None = Query(None)):
    df = _load_df_for_version(version)
    return reports.regional_performance(df)


@app.get("/reports/product-analysis")
def get_product_analysis(version: str | None = Query(None), top_n: int = 10, sort_by: str = Query("total_arrecadado")):
    df = _load_df_for_version(version)
    return reports.product_analysis(df, top_n=top_n, sort_by=sort_by)


@app.get("/reports/customer-profile")
def get_customer_profile(version: str | None = Query(None)):
    df = _load_df_for_version(version)
    return reports.customer_profile(df)


@app.get("/reports/financial-metrics")
def get_financial_metrics(version: str | None = Query(None)):
    df = _load_df_for_version(version)
    return reports.financial_metrics(df)