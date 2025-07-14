import pandas as pd
from sklearn.preprocessing import StandardScaler
from scipy.cluster.hierarchy import linkage, dendrogram
import matplotlib.pyplot as plt
import os

# --- Carregar dados ---
df = pd.read_csv("data/dados_agrupamento.csv")

# --- Agrupar por companhia aérea ---
df_grouped = df.groupby("Airline").agg({
    "ArrDelay": "mean",
    "Distance": "mean"
}).dropna()

# --- Normalizar os dados ---
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_grouped)

# --- Gerar dendrograma ---
linked = linkage(X_scaled, method='ward')

plt.figure(figsize=(12, 6))
dendrogram(
    linked,
    labels=df_grouped.index.tolist(),
    leaf_rotation=90,
    leaf_font_size=10
)

plt.title("Dendrograma - Companhias Aéreas por Atraso Médio e Distância Média")
plt.xlabel("Companhias Aéreas")
plt.ylabel("Distância (Ward linkage)")
plt.tight_layout()

# --- Salvar gráfico ---
os.makedirs("graficos", exist_ok=True)
plt.savefig("graficos/dendrograma_companhias.png", dpi=300, bbox_inches="tight")
plt.show()
