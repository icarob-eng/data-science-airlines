import pandas as pd

path = '../data/Combined_Flights_2019.parquet'

df_raw = pd.read_parquet(path)

# Se necessário, selecione apenas as colunas desejadas
colunas_necessarias = [
    "Airline", "Cancelled", "ArrDelay", "OriginCityName", "DestCityName",
    "Distance", "Month", "DayofMonth", "DayOfWeek", "ArrTime"
]
df_raw = df_raw[colunas_necessarias]

# Ajustes para manter compatibilidade com o restante do código
df_raw.rename(columns={'DayofMonth': 'DayOfMonth'}, inplace=True)
df_raw.dropna(subset=["Airline", "OriginCityName", "DestCityName", "Distance"], inplace=True)
df_raw.fillna(0, inplace=True)
df_raw.to_parquet('../data/reduced_Combined_Flights_2019(1).parquet', compression='brotli')
