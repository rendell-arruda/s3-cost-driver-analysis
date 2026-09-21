import pandas as pd
import numpy as np

np.random.seed(42)

buckets = ["logs-prod", "backups-eu", "data-lake-raw", "app-assets", "ml-datasets"]
prefixos = ["2023/", "2024/", "raw/", "processed/", "archive/"]
storage_classes = ["STANDARD", "STANDARD_IA", "GLACIER", "GLACIER_DEEP_ARCHIVE"]
regioes = ["us-east-1", "sa-east-1"]

precos_por_regiao = {
    "us-east-1": {
        "STANDARD": 0.023,
        "STANDARD_IA": 0.0125,
        "GLACIER": 0.0036,
        "GLACIER_DEEP_ARCHIVE": 0.00099,
    },
    "sa-east-1": {
        "STANDARD": 0.0405,
        "STANDARD_IA": 0.0125 * 2.1,  # estimativa, sem fonte oficial confirmada
        "GLACIER": 0.0085,
        "GLACIER_DEEP_ARCHIVE": 0.00099 * 2.1,  # estimativa
    },
}

# --- Linhas normais (ruído de fundo) ---
n = 300
dados = {
    "bucket": np.random.choice(buckets, n),
    "prefixo": np.random.choice(prefixos, n),
    "regiao": np.random.choice(regioes, n, p=[0.6, 0.4]),
    "storage_class": np.random.choice(storage_classes, n, p=[0.4, 0.25, 0.25, 0.1]),
    "tamanho_gb": np.round(np.random.uniform(1, 200, n), 2),
    "idade_dias": np.random.randint(1, 400, n),
    "num_objetos": np.random.randint(10, 3000, n),
}
df = pd.DataFrame(dados)

# --- Caso escondido 1: bucket "vilão" (logs-prod, us-east-1, STANDARD, bem antigo) ---
vilao = pd.DataFrame(
    {
        "bucket": ["logs-prod"] * 15,
        "prefixo": ["2023/"] * 15,
        "regiao": ["us-east-1"] * 15,
        "storage_class": ["STANDARD"] * 15,
        "tamanho_gb": np.round(np.random.uniform(300, 600, 15), 2),
        "idade_dias": np.random.randint(700, 900, 15),
        "num_objetos": np.random.randint(1000, 5000, 15),
    }
)

# --- Caso escondido 2: bucket grande mas barato (já otimizado) ---
otimizado = pd.DataFrame(
    {
        "bucket": ["data-lake-raw"] * 10,
        "prefixo": ["archive/"] * 10,
        "regiao": ["us-east-1"] * 10,
        "storage_class": ["GLACIER_DEEP_ARCHIVE"] * 10,
        "tamanho_gb": np.round(np.random.uniform(800, 1500, 10), 2),
        "idade_dias": np.random.randint(500, 900, 10),
        "num_objetos": np.random.randint(2000, 8000, 10),
    }
)

# --- Caso escondido 3: prefixo caro em sa-east-1 (a região mais cara!) ---
prefixo_caro = pd.DataFrame(
    {
        "bucket": ["ml-datasets"] * 12,
        "prefixo": ["raw/"] * 12,
        "regiao": ["sa-east-1"] * 12,
        "storage_class": ["STANDARD"] * 12,
        "tamanho_gb": np.round(np.random.uniform(100, 250, 12), 2),
        "idade_dias": np.random.randint(600, 800, 12),
        "num_objetos": np.random.randint(500, 2000, 12),
    }
)

df = pd.concat([df, vilao, otimizado, prefixo_caro], ignore_index=True)

# Calcula o preço por GB combinando região + storage class (linha a linha)
df["preco_por_gb"] = df.apply(
    lambda linha: precos_por_regiao[linha["regiao"]][linha["storage_class"]], axis=1
)

df["custo_mensal_usd"] = np.round(df["tamanho_gb"] * df["preco_por_gb"], 2)

df.to_csv("dados_s3_sinteticos.csv", index=False)
print(f"Dataset gerado com {len(df)} linhas.")
print(df.head())
