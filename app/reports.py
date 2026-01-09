from typing import Dict, Any
import pandas as pd
from app.business import calcular_receita_liquida_e_lucro_bruto, calcular_metricas_transacao


def sales_summary(df: pd.DataFrame) -> Dict[str, Any]:
    # usa lógica centralizada para métricas financeiras e de transação
    fin = calcular_receita_liquida_e_lucro_bruto(df)
    trans = calcular_metricas_transacao(df)
    total_items = int(df["quantidade"].sum()) if "quantidade" in df.columns else 0
    return {
        "total_vendas": float(fin["receita_liquida"]),
        "custo_total": float(fin["custo_total"]),
        "lucro_bruto": float(fin["lucro_bruto"]),
        "numero_transacoes": int(trans["numero_transacoes"]),
        "media_por_transacao": float(trans["media_por_transacao"]),
        "itens_totais": total_items,
    }


def regional_performance(df: pd.DataFrame, top_n: int = 10) -> Dict[str, Any]:
    grp = df.groupby("regiao").agg({"valor_final": "sum", "id_transacao": "nunique"}).rename(columns={"id_transacao": "orders"})
    grp = grp.sort_values("valor_final", ascending=False)
    return {"por_regiao": grp.reset_index().to_dict(orient="records")}


def product_analysis(df: pd.DataFrame, top_n: int = 10, sort_by: str = "total_arrecadado") -> Dict[str, Any]:
    # agrupa por produto e calcula quantidade vendida e total arrecadado
    grp = df.groupby(["produto_id", "nome_produto"]).agg({"valor_final": "sum", "quantidade": "sum"}).reset_index()
    grp = grp.rename(columns={"valor_final": "total_arrecadado", "quantidade": "quantidade_vendida"})

    # escolher coluna de ordenação
    if sort_by not in {"total_arrecadado", "quantidade_vendida", "nome_produto"}:
        sort_by = "total_arrecadado"

    ascending = False if sort_by in {"total_arrecadado", "quantidade_vendida"} else True
    grp = grp.sort_values(sort_by, ascending=ascending)

    records = grp.head(top_n)[["produto_id", "nome_produto", "quantidade_vendida", "total_arrecadado"]].to_dict(orient="records")
    return {"produtos": records}


def customer_profile(df: pd.DataFrame) -> Dict[str, Any]:
    age_stats = df["idade_cliente"].describe().to_dict() if "idade_cliente" in df.columns else {}
    gender = df["genero_cliente"].value_counts().to_dict() if "genero_cliente" in df.columns else {}
    top_customers = df.groupby(["cliente_id", "nome_cliente"]).agg({"valor_final": "sum"}).sort_values("valor_final", ascending=False).head(10).reset_index().to_dict(orient="records")
    return {"estatisticas_idade": age_stats, "distribuicao_genero": gender, "principais_clientes": top_customers}


def financial_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    # usar funções centralizadas de negócio para garantir consistência
    from app.business import calcular_receita_liquida_e_lucro_bruto

    fin = calcular_receita_liquida_e_lucro_bruto(df)
    # garantir números (floats)
    receita_liquida = float(fin.get("receita_liquida", 0.0))
    custo_total = float(fin.get("custo_total", 0.0))
    lucro_bruto = float(fin.get("lucro_bruto", 0.0))
    return {"lucro_bruto": lucro_bruto, "receita_liquida": receita_liquida, "custo_total": custo_total}