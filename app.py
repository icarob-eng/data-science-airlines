import streamlit as st
import pandas as pd
from plotly import express as px
import os


COLORS = {
    'number': "#AEC6CF",
    'delay': "#FFB347",
    'dist': "#77DD77",
    'cancel': "#FF6961",
    # 'gray': "#CFCFC4",  # cores não usadas
    # 'purple': "#B39EB5",
    # 'pink': "#FFD1DC",
    # 'yellow': "#FDFD96",
    # 'lavender': "#CB99C9"
}

# --- Configuração da página ---
st.set_page_config(page_title="Análise de Voos 2019", layout="wide")

# --- Cabeçalho ---
st.title("Análise de Voos - EUA - Ano 2019")
st.text("Use o menu lateral para navegar entre análises.")

# --- Menu lateral ---
st.sidebar.title("Menu de Análises")
opcao = st.sidebar.radio("Selecione um tópico de análise:", [
    "Visão Geral",
    "Por linhas aéreas",
    "Geográfica",
    "Temporal"
])

# --- Carregar dados ---
data_dir = 'data'
csv_path = os.path.join(data_dir, 'reduced2019.csv')

@st.cache_data
def carregar_dados(path):
    df_raw = pd.read_csv(path, usecols=[
        "Airline", 'Cancelled', "ArrDelay", "OriginCityName", "DestCityName",
        'Distance', 'Month', 'DayofMonth', 'DayOfWeek', 'ArrTime'])
    df_raw.rename(columns={'DayofMonth': 'DayOfMonth'}, inplace=True)
    df_raw.dropna(subset=["Airline"], inplace=True)
    df_raw.dropna(subset=["OriginCityName"], inplace=True)
    df_raw.dropna(subset=["DestCityName"], inplace=True)
    df_raw.dropna(subset=["Distance"], inplace=True)
    df_raw.fillna(0, inplace=True)
    return df_raw


def format_number(number):
    if int(number) != number:
        return f"{number:.2f}"
    return f'{number:,}'


def _chart_hbar(fig):
    '''Implementa firulas estéticas e plota para gráfico de barras horizontais'''
    fig.update_layout(
        xaxis={'range': [0, None], 'fixedrange': True},
        yaxis={'tickmode': 'linear', 'fixedrange': True}
    )
    st.plotly_chart(fig)

def _chart_bar(fig):
    '''Implementa firulas estéticas e plota para gráfico de barras verticais'''
    fig.update_layout(
        yaxis={'range': [0, None], 'fixedrange': True},
        xaxis={'tickmode': 'linear', 'fixedrange': True}
    )
    st.plotly_chart(fig)


if os.path.exists(csv_path):
    df = carregar_dados(csv_path)

    # --- Exibir visualizações conforme opção escolhida ---
    match opcao:
        case "Visão Geral":
            st.subheader("Visão Geral do Dataset")

            st.text('Dataset em números:')
            cols = st.columns(3)
            with cols[0]:
                st.metric('Linhas aéreas', len(df['Airline'].unique()), border=True)
            with cols[1]:
                st.metric('Cidades', len(df['DestCityName'].unique()), border=True)
            with cols[2]:
                st.metric('Total de voos', format_number(len(df)), border=True)

            st.text('10 voos aleatórios:')
            st.dataframe(df.sample(10))
            st.write(df.describe())

        case "Por linhas aéreas":
            st.sidebar.subheader('Selecione métricas de análise')

            metricas = {
                'num': st.sidebar.checkbox('Número de voos'),
                'dist': st.sidebar.checkbox('Distância média'),
                'delay': st.sidebar.checkbox('Atraso médio'),
                'cancel': st.sidebar.checkbox('Cancelamentos')
                # TODO: Voos vs atraso médio por companhia

            }

            voos_por_companhia = df['Airline'].value_counts().reset_index().rename(
                columns={'count': 'TotalVoos'}).sort_values('TotalVoos')

            if metricas['num']:
                st.subheader('Ranking de companhias aéreas:')
                _chart_hbar(px.bar(
                    data_frame=voos_por_companhia,
                    labels={'Airline': 'Linha aérea', 'TotalVoos': 'Número de voos'},
                    x='TotalVoos', y='Airline',
                    orientation='h', color_discrete_sequence=[COLORS['number']],
                ))
            if metricas['dist']:
                st.subheader('Companhias aéreas com rotas mais longas:')

                _chart_hbar(px.bar(
                    data_frame=df.groupby('Airline')['Distance'].mean().sort_values(),
                    labels={'Airline': 'Linha aérea', 'Distance': 'Distância média [milhas]'},
                    x='Distance',
                    orientation='h', color_discrete_sequence=[COLORS['dist']],
                ))
            if metricas['delay']:
                st.subheader('Atraso médio de chegada por companhia:')

                _chart_hbar(px.bar(
                    data_frame=df.groupby('Airline')['ArrDelay'].mean().sort_values(),
                    labels={'Airline': 'Linha aérea', 'ArrDelay': 'Atraso médio [min]'},
                    x='ArrDelay',
                    orientation='h', color_discrete_sequence=[COLORS['delay']],
                ))
            if metricas['cancel']:
                st.subheader('Companhias aéreas que mais cancelam:')

                cancel_counts = (df[df['Cancelled'] == True]['Airline']
                                 .value_counts()
                                 .reset_index()
                                 .rename(columns={'count': 'VoosCancelados'}))
                cancel_counts['VoosCanceladosPct'] = cancel_counts['VoosCancelados'] / \
                                                                 voos_por_companhia['TotalVoos'] * 100

                cols = st.columns(2)
                with cols[0]:
                    st.metric('Total de voos cancelados nos EUA no ano de 2019',
                              value=format_number(cancel_counts['VoosCancelados'].sum()), border=True)
                with cols[1]:
                    st.metric('Cancelamentos a cada 100 voos',
                              value=format_number(cancel_counts['VoosCanceladosPct'].sum()))

                _chart_hbar(px.bar(
                    data_frame=cancel_counts.sort_values(by='VoosCanceladosPct'),
                    labels={'Airline': 'Linha aérea', 'VoosCanceladosPct': 'Cancelamentos a cada 100 voos'},
                    x='VoosCanceladosPct', y='Airline',
                    orientation='h', color_discrete_sequence=[COLORS['cancel']],
                ))

        case "Geográfica":
            st.sidebar.subheader('Selecione métricas de análise')

            metricas = {
                'faixas': st.sidebar.checkbox('Relação atraso e distância'),
                'cidades-companhias': st.sidebar.checkbox('Principais cidades por companhia'),
                # TODO: Voos vs atraso médio por cidade
                # TODO: top cidades com mais atrasos
            }

            if metricas['faixas']:
                st.subheader('O atraso dos voos depende da distância?')
                bins = [0, 250, 500, 750, 1000, 1250, 1500, 2000, 3000, 4000, 5000]
                labels = ['0–250', '251–500', '501–750', '751–1000', '1001–1250', '1251–1500',
                          '1501–2000', '2001–3000', '3001–4000', '4001–5000']

                df['FaixaDistancia'] = pd.cut(df['Distance'], bins=bins, labels=labels)

                _chart_bar(px.bar(
                    data_frame=df.groupby('FaixaDistancia', observed=False)['ArrDelay'].mean().reset_index(),
                    labels={'FaixaDistancia': 'Faixa de distância [milhas]', 'ArrDelay': 'Atraso de chegada [min]'},
                    x='FaixaDistancia', y='ArrDelay', color_discrete_sequence=[COLORS['delay']],
                ))


            if metricas['cidades-companhias']:
                st.subheader('Top 10 cidades destino por companhia')
                comp = st.selectbox('Companhia:', options=sorted(df['Airline'].unique().tolist()))

                _chart_hbar(px.bar(
                    data_frame=df[df['Airline'] == comp]['DestCityName'].value_counts(ascending=True).head(10),
                    labels={'DestCityName': 'Cidade', 'count': f'Voos da "{comp}" com destino a esta cidade'},
                    x='count',
                    orientation='h', color_discrete_sequence=[COLORS['number']],
                ))

        case 'Temporal':
            st.subheader('Análise temporal')
            cols = st.columns(2)
            with cols[0]:
                scale = st.select_slider('Escala temporal:', options=['Ano', 'Mês', 'Semana', 'Dia'])
            with cols[1]:
                metrica = st.radio('Métrica:', options=['Voos', 'Atrasos', 'Cancelamentos'])


            key = {
                'Ano': 'Month',
                'Mês': 'DayOfMonth',
                'Semana': 'DayOfWeek',
                'Dia': 'HourBlock',
            }[scale]

            label = {
                'Ano': 'Mês',
                'Mês': 'Dia do mês',
                'Semana': 'Dia da semana',
                'Dia': 'Bloco de hora',
            }[scale]


            if scale == 'Mês':
                with st.columns([0.5, 0.5])[0]:
                    month = st.selectbox('Mês do ano:', options=['Todos', *range(1,13)])
                if month != 'Todos':
                    df = df[df['Month'] == month]

            if scale == 'Dia': df['HourBlock'] = df['ArrTime'] // 100

            if metrica == 'Cancelamentos':
                df = df[df['Cancelled'] == True]

            gb = df.groupby(key)

            match metrica:
                case 'Voos':
                    st.subheader(f'Número total de voos por {label}')
                    _chart_bar(px.bar(
                        data_frame=gb.size().reset_index(name='count'),
                        labels={key: label, 'count': 'Número de voos'},
                        x=key, y='count',
                        color_discrete_sequence=[COLORS['number']]
                    ))
                case 'Atrasos':
                    st.subheader(f'Atraso de chegada médio por {label}')
                    _chart_bar(px.bar(
                        data_frame=gb['ArrDelay'].mean().reset_index(name='count'),
                        labels={key: label, 'count': 'Tempo médio de atraso [min]'},
                        x=key, y='count',
                        color_discrete_sequence=[COLORS['delay']]
                    ))
                case 'Cancelamentos':
                    st.subheader(f'Número total de cancelamentos por {label}')
                    _chart_bar(px.bar(
                        data_frame=gb.size().reset_index(name='count'),
                        labels={key: label, 'count': 'Número de cancelamentos'},
                        x=key, y='count',
                        color_discrete_sequence=[COLORS['cancel']]
                    ))

else:
    st.error("Arquivo de dados 'reduced2019.csv' não encontrado.")
