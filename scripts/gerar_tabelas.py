import pandas as pd

datapath = '../data/'
outpath = '../tables/'

df = pd.read_parquet(datapath + 'reduced_Combined_Flights_2019.parquet')

# metricas gerais
pd.DataFrame({
    'Names': ['nAirlines', 'nCities', 'nFlights'],
    'Values': [len(df['Airline'].unique()), len(df['DestCityName'].unique()), len(df)]
}).to_csv(outpath + 'metricas_gerais.csv', index=False)

# sample
df.sample(100).to_csv(outpath + '100samples.csv')


# bunch of things

voos_por_companhia = df['Airline'].value_counts().reset_index().rename(columns={'count': 'TotalVoos'}).sort_values('TotalVoos')
top_companhias = voos_por_companhia.tail(5).Airline
voos_por_companhia.to_csv(outpath + 'voos_por_companhia.csv', index=False)

voos_por_cidade = df['DestCityName'].value_counts().reset_index().rename(columns={'count': 'TotalVoos'}).sort_values('TotalVoos')
top_cities = voos_por_cidade.tail(10).DestCityName
voos_por_cidade.to_csv(outpath + 'voos_por_cidade.csv', index=False)

# flights_top = df[df['Airline'].isin(top_companhias)][df['DestCityName'].isin(top_cities)]


# distancia por companhia
df.groupby('Airline')['Distance'].mean().sort_values().to_csv(outpath + 'dist_por_comp.csv', index=False)

# atraso medio por companhia
df.groupby('Airline')['ArrDelay'].mean().sort_values().to_csv(outpath + 'atrasi_por_comp.csv', index=False)

# cancelamentos idk
cancel_counts = (df[df['Cancelled'] == True]['Airline']
                             .value_counts()
                             .reset_index()
                             .rename(columns={'count': 'VoosCancelados'}))
cancel_counts['VoosCanceladosPct'] = cancel_counts['VoosCancelados'] / voos_por_companhia['TotalVoos'] * 100
cancel_counts.to_csv(outpath + 'cancel_counts.csv', index=False)

# idk
df_voos_delay = df.groupby('Airline').agg(
    {'ArrDelay': 'mean'}
).rename(columns={'ArrDelay': 'AtrasoMedio'}).reset_index()

df_voos_delay['NumVoos'] = df['Airline'].value_counts().reindex(df_voos_delay['Airline']).values
df_voos_delay.to_csv(outpath + 'voos_delay.csv', index=False)


# atrasos por faixa de distância
bins = [0, 250, 500, 750, 1000, 1250, 1500, 2000, 3000, 4000, 5000]
labels = ['0–250', '251–500', '501–750', '751–1000', '1001–1250', '1251–1500',
          '1501–2000', '2001–3000', '3001–4000', '4001–5000']

df['FaixaDistancia'] = pd.cut(df['Distance'], bins=bins, labels=labels)
df.groupby('FaixaDistancia', observed=False)['ArrDelay'].mean().reset_index().to_csv(outpath + 'atrasos_por_faixa.csv', index=False)


for comp in voos_por_companhia['Airline']:
    df[df['Airline'] == comp]['DestCityName'].value_counts(ascending=True).head(10).to_csv(outpath + f'comps/{comp.split(' ')[0]}_destinos.csv', index=False)

# voos atrasados por cidade
df.groupby('DestCityName').agg({
                'ArrDelay': 'mean',
                'Airline': 'count'
            }).rename(columns={
                'ArrDelay': 'AtrasoMedio',
                'Airline': 'NumVoos'
            }).reset_index().to_csv(outpath + f'atrasos_por_cidade.csv', index=False)


# cidades com mais atrasos
(df.groupby('DestCityName')['ArrDelay']
 .mean()
 .sort_values(ascending=False)
 .head(10)
 .reset_index()
 .rename(columns={'ArrDelay': 'AtrasoMedio'})
 .sort_values(by='AtrasoMedio').to_csv(outpath + f'city_delay.csv', index=False)
)
