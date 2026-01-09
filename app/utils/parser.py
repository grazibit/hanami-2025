from typing import Tuple, List
import pandas as pd
from pathlib import Path
from app.config import REQUIRED_COLUMNS


def read_file(file_path: Path) -> pd.DataFrame:
    if file_path.suffix.lower() in (".xls", ".xlsx"):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path, low_memory=False)
    return df


def validate_and_normalize(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    errors: List[str] = []

    # normalize columns to lowercase
    df.columns = [c.strip().lower() for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        # columns missing is critical: raise explicit error
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")

    # Type conversions and basic cleaning
    # Dates
    df["data_venda"] = pd.to_datetime(df["data_venda"], errors="coerce")

    # Numeric fields
    num_cols = [
        "preco_unitario",
        "quantidade",
        "subtotal",
        "desconto_percent",
        "desconto_valor",
        "valor_final",
        "renda_estimada",
        "tempo_entrega_dias",
        "margem_lucro",
        "idade_cliente",
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Limpeza de nulos em colunas críticas: remover linhas sem id_transacao ou valor_final
    if "id_transacao" in df.columns:
        before = len(df)
        df = df[df["id_transacao"].notna()]
        after = len(df)
        if after < before:
            errors.append(f"Removidas {before-after} linhas sem id_transacao")

    if "valor_final" in df.columns:
        before = len(df)
        df = df[df["valor_final"].notna()]
        after = len(df)
        if after < before:
            errors.append(f"Removidas {before-after} linhas sem valor_final")
    else:
        # should not happen due to earlier missing check, but keep safe
        raise ValueError("Coluna 'valor_final' não encontrada")

    # Preencher idade_cliente com mediana quando ausente
    if "idade_cliente" in df.columns:
        median_age = int(df["idade_cliente"].median(skipna=True)) if not df["idade_cliente"].dropna().empty else 0
        df["idade_cliente"] = df["idade_cliente"].fillna(median_age).astype(int)

    # Padronização de campos textuais
    text_cols = [
        "canal_venda",
        "forma_pagamento",
        "cidade_cliente",
        "estado_cliente",
        "nome_produto",
        "categoria",
        "marca",
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower()

    # Validate ranges for desconto_percent (0-100)
    if "desconto_percent" in df.columns:
        invalid_discount = df[~df["desconto_percent"].between(0, 100, inclusive="both") & df["desconto_percent"].notna()]
        if not invalid_discount.empty:
            errors.append(f"desconto_percent com valores fora do intervalo 0-100: {len(invalid_discount)} linhas")

    # Check for negative prices or quantities
    if "preco_unitario" in df.columns and (df["preco_unitario"] < 0).any():
        errors.append("preco_unitario contém valores negativos")
    if "quantidade" in df.columns and (df["quantidade"] < 0).any():
        errors.append("quantidade contém valores negativas")

    return df, errors
