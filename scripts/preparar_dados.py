import pandas as pd
import os

# --- Carregar dados do Parquet ---
df = pd.read_parquet("data/reduced_Combined_Flights_2019.parquet")

# --- Selecionar colunas relevantes ---
colunas_utilizadas = [
    "Airline",      # Categórica → será codificada depois
    "Distance",     # Numérica
    "ArrDelay",     # Numérica
    "Cancelled",     # Para filtragem
    "Month" 
]
df = df[colunas_utilizadas]

# --- Filtrar voos não cancelados e remover valores ausentes ---
df = df[df["Cancelled"] == False]
df = df.drop(columns=["Cancelled"])
df = df.dropna()

# --- Salvar dataset limpo para o agrupamento ---
os.makedirs("data", exist_ok=True)
df.to_csv("data/dados_agrupamento.csv", index=False)

print("✅ Dados preparados com sucesso e salvos em 'data/dados_agrupamento.csv'")
