from typing import Dict
import pandas as pd


def calcular_receita_liquida_e_lucro_bruto(df: pd.DataFrame) -> Dict[str, float]:
    """Calcula receita líquida e lucro bruto a partir do DataFrame.

    - `receita_liquida`: soma de `valor_final`.
    - `custo_total`: se `custo_produto` existir usa soma, senão tenta estimar por `preco_unitario * quantidade * (1 - margem_lucro)` ou `preco_unitario * quantidade`.
    - `lucro_bruto`: `receita_liquida - custo_total`.

    Retorna dicionário com `receita_liquida`, `custo_total`, `lucro_bruto`.
    """
    receita = float(df["valor_final"].sum()) if "valor_final" in df.columns else 0.0

    if "custo_produto" in df.columns and not df["custo_produto"].isna().all():
        custo_total = float(df["custo_produto"].sum())
    else:
        # tentar estimar custo usando margem_lucro quando disponível
        if "preco_unitario" in df.columns and "quantidade" in df.columns and "margem_lucro" in df.columns:
            # margem_lucro representa fração (ex: 0.2 == 20%) — custo = valor_final * (1 - margem)
            # usamos preco_unitario*quantidade como proxy do valor bruto
            bruto = (df["preco_unitario"].fillna(0.0) * df["quantidade"].fillna(0)).sum()
            # quando margem disponível, estimamos custo como bruto * (1 - margem média)
            margem_media = df["margem_lucro"].dropna().mean() if not df["margem_lucro"].dropna().empty else 0.0
            custo_total = float(bruto * (1.0 - float(margem_media)))
        elif "preco_unitario" in df.columns and "quantidade" in df.columns:
            custo_total = float((df["preco_unitario"].fillna(0.0) * df["quantidade"].fillna(0)).sum())
        else:
            custo_total = 0.0

    lucro_bruto = receita - custo_total
    return {"receita_liquida": receita, "custo_total": custo_total, "lucro_bruto": lucro_bruto}


def calcular_metricas_transacao(df: pd.DataFrame) -> Dict[str, float]:
    """Calcula total de vendas, média por transação e número de transações.

    - `total_vendas`: soma de `valor_final`.
    - `numero_transacoes`: número de transações únicas por `id_transacao` ou número de linhas.
    - `media_por_transacao`: `total_vendas / numero_transacoes` (0 se none).
    """
    total_vendas = float(df["valor_final"].sum()) if "valor_final" in df.columns else 0.0
    if "id_transacao" in df.columns:
        num_transacoes = int(df["id_transacao"].nunique())
    else:
        num_transacoes = int(len(df))
    media = float(total_vendas / num_transacoes) if num_transacoes else 0.0
    return {"total_vendas": total_vendas, "media_por_transacao": media, "numero_transacoes": num_transacoes}
