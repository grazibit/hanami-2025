from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EXPORTS_DIR = BASE_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"

REQUIRED_COLUMNS = [
    "id_transacao",
    "data_venda",
    "valor_final",
    "subtotal",
    "desconto_percent",
    "desconto_valor",
    "canal_venda",
    "forma_pagamento",
    "cliente_id",
    "nome_cliente",
    "idade_cliente",
    "genero_cliente",
    "cidade_cliente",
    "estado_cliente",
    "renda_estimada",
    "produto_id",
    "nome_produto",
    "categoria",
    "marca",
    "preco_unitario",
    "quantidade",
    "margem_lucro",
    "regiao",
    "status_entrega",
    "tempo_entrega_dias",
    "vendedor_id",
]

EXPORTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
