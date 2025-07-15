import streamlit as st
import pandas as pd
from plotly import express as px
import joblib

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
    # "Temporal",
    "Classificação de Atraso"
])

@st.cache_data
def carregar_dados(path):
    try:
        return pd.read_csv(path)
    except Exception:
        return st.error("Erro ao carregar dados.")

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

# --- Exibir visualizações conforme opção escolhida ---
match opcao:
    case "Visão Geral":
        st.subheader("Visão Geral do Dataset")

        st.text('Dataset em números:')

        dados_gerais = carregar_dados('tables/metricas_gerais.csv')

        cols = st.columns(3)
        with cols[0]:
            st.metric('Linhas aéreas', dados_gerais.Values[0], border=True)
        with cols[1]:
            st.metric('Cidades', dados_gerais.Values[1], border=True)
        with cols[2]:
            st.metric('Total de voos', format_number(dados_gerais.Values[2]), border=True)

        st.text('10 voos aleatórios:')

        df = carregar_dados('tables/100samples.csv')
        st.dataframe(df.sample(10))
        st.write(df.describe())

    case "Por linhas aéreas":
        st.sidebar.subheader('Selecione métricas de análise')

        metricas = {
            'num': st.sidebar.checkbox('Número de voos'),
            'dist': st.sidebar.checkbox('Distância média'),
            'delay': st.sidebar.checkbox('Atraso médio'),
            'cancel': st.sidebar.checkbox('Cancelamentos'),
            'voos_vs_delay': st.sidebar.checkbox('Atraso médio vs N° de voos')
        }

        voos_por_companhia = carregar_dados('tables/voos_por_companhia.csv')

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
                data_frame=carregar_dados('tables/dist_por_comp.csv'),
                labels={'Airline': 'Linha aérea', 'Distance': 'Distância média [milhas]'},
                x='Distance',
                orientation='h', color_discrete_sequence=[COLORS['dist']],
            ))
        if metricas['delay']:
            st.subheader('Atraso médio de chegada por companhia:')

            _chart_hbar(px.bar(
                data_frame=carregar_dados('tables/atrasi_por_comp.csv'),
                labels={'Airline': 'Linha aérea', 'ArrDelay': 'Atraso médio [min]'},
                x='ArrDelay',
                orientation='h', color_discrete_sequence=[COLORS['delay']],
            ))
        if metricas['cancel']:
            st.subheader('Companhias aéreas que mais cancelam:')

            cancel_counts = carregar_dados('tables/cancel_counts.csv')

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
        if metricas['voos_vs_delay']:
            st.subheader('Atraso médio com relação ao número de voos (Top 10 companhias)')

            df_voos_delay = carregar_dados('tables/voos_delay.csv')

            df_voos_delay_top10 = df_voos_delay.nlargest(10, 'NumVoos')

            fig = px.scatter(
                df_voos_delay_top10,
                x='NumVoos',
                y='AtrasoMedio',
                text='Airline',
                size='NumVoos',
                color_discrete_sequence=[COLORS['delay']],
                labels={
                    'NumVoos': 'Número de voos',
                    'AtrasoMedio': 'Atraso médio (min)',
                    'Airline': 'Companhia'
                },
                title='Top 10 companhias: Nº de voos vs Atraso médio'
            )
            fig.update_traces(textposition='top center')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)


    case "Geográfica":
        st.sidebar.subheader('Selecione métricas de análise')

        metricas = {
            'faixas': st.sidebar.checkbox('Relação atraso e distância'),
            'cidades-companhias': st.sidebar.checkbox('Principais cidades por companhia'),
            'voos_vs_delay_city': st.sidebar.checkbox('Relação entre atraso e número de voos'),
            'city-delay': st.sidebar.checkbox('Principais cidades por atrasos'),
        }

        if metricas['faixas']:
            st.subheader('O atraso dos voos depende da distância?')

            _chart_bar(px.bar(
                data_frame=carregar_dados('tables/atrasos_por_faixa.csv'),
                labels={'FaixaDistancia': 'Faixa de distância [milhas]', 'ArrDelay': 'Atraso de chegada [min]'},
                x='FaixaDistancia', y='ArrDelay', color_discrete_sequence=[COLORS['delay']],
            ))


        if metricas['cidades-companhias']:
            st.subheader('Top 10 cidades destino por companhia')

            voos_por_companhia = carregar_dados('tables/voos_por_companhia.csv')
            comp = st.selectbox('Companhia:', options=sorted(voos_por_companhia['Airline']))

            _chart_hbar(px.bar(
                data_frame=carregar_dados(f'tables/comps/{comp.split(' ')[0]}_destinos.csv'),
                labels={'DestCityName': 'Cidade', 'count': f'Voos da "{comp}" com destino a esta cidade'},
                x='count',
                orientation='h', color_discrete_sequence=[COLORS['number']],
            ))

        if metricas['voos_vs_delay_city']:
            st.subheader('Relação entre número de voos e atraso médio por cidade de destino')

            df_voos_delay_cidade = carregar_dados('tables/atrasos_por_cidade.csv')

            df_voos_delay_cidade_top = df_voos_delay_cidade.nlargest(15, 'NumVoos')

            _chart_hbar(px.scatter(
                df_voos_delay_cidade_top,
                x='NumVoos',
                y='AtrasoMedio',
                size='NumVoos',
                text='DestCityName',
                color_discrete_sequence=[COLORS['delay']],
                labels={
                    'NumVoos': 'Número de voos',
                    'AtrasoMedio': 'Atraso médio [min]',
                    'DestCityName': 'Cidade de destino'
                },
                title='Relação entre número de voos e atraso médio por cidade'
            ))

        if metricas['city-delay']:
            st.subheader('Top 10 cidades com maiores atrasos médios de chegada')

            df_city_delay = carregar_dados('tables/city_delay.csv')

            _chart_hbar(px.bar(
                data_frame=df_city_delay.sort_values(by='AtrasoMedio'),  # menor para cima
                x='AtrasoMedio',
                y='DestCityName',
                orientation='h',
                color_discrete_sequence=[COLORS['delay']],
                labels={
                    'DestCityName': 'Cidade de destino',
                    'AtrasoMedio': 'Atraso médio [min]'
                },
                title='Top 10 cidades com maiores atrasos médios'
            ))
    # case 'Temporal':
    #     st.subheader('Análise temporal')
    #     cols = st.columns(2)
    #     with cols[0]:
    #         scale = st.select_slider('Escala temporal:', options=['Ano', 'Mês', 'Semana', 'Dia'])
    #     with cols[1]:
    #         metrica = st.radio('Métrica:', options=['Voos', 'Atrasos', 'Cancelamentos'])
    #
    #
    #     key = {
    #         'Ano': 'Month',
    #         'Mês': 'DayOfMonth',
    #         'Semana': 'DayOfWeek',
    #         'Dia': 'HourBlock',
    #     }[scale]
    #
    #     label = {
    #         'Ano': 'Mês',
    #         'Mês': 'Dia do mês',
    #         'Semana': 'Dia da semana',
    #         'Dia': 'Bloco de hora',
    #     }[scale]
    #
    #
    #     if scale == 'Mês':
    #         with st.columns([0.5, 0.5])[0]:
    #             month = st.selectbox('Mês do ano:', options=['Todos', *range(1,13)])
    #         if month != 'Todos':
    #             df = df[df['Month'] == month]
    #
    #     if scale == 'Dia': df['HourBlock'] = df['ArrTime'] // 100
    #
    #     if metrica == 'Cancelamentos':
    #         df = df[df['Cancelled'] == True]
    #
    #     gb = df.groupby(key)
    #
    #     match metrica:
    #         case 'Voos':
    #             st.subheader(f'Número total de voos por {label}')
    #             _chart_bar(px.bar(
    #                 data_frame=gb.size().reset_index(name='count'),
    #                 labels={key: label, 'count': 'Número de voos'},
    #                 x=key, y='count',
    #                 color_discrete_sequence=[COLORS['number']]
    #             ))
    #         case 'Atrasos':
    #             st.subheader(f'Atraso de chegada médio por {label}')
    #             _chart_bar(px.bar(
    #                 data_frame=gb['ArrDelay'].mean().reset_index(name='count'),
    #                 labels={key: label, 'count': 'Tempo médio de atraso [min]'},
    #                 x=key, y='count',
    #                 color_discrete_sequence=[COLORS['delay']]
    #             ))
    #         case 'Cancelamentos':
    #             st.subheader(f'Número total de cancelamentos por {label}')
    #             _chart_bar(px.bar(
    #                 data_frame=gb.size().reset_index(name='count'),
    #                 labels={key: label, 'count': 'Número de cancelamentos'},
    #                 x=key, y='count',
    #                 color_discrete_sequence=[COLORS['cancel']]
    #             ))
    case "Classificação de Atraso":
        st.subheader("Previsão de Atraso de Voo")

        # Carregar modelo e transformadores
        modelo = joblib.load("modelo/classificador_voos.pkl")
        scaler = joblib.load("modelo/scaler_classificacao.pkl")
        encoder = joblib.load("modelo/encoder_airline_classificacao.pkl")
        colunas_usadas = joblib.load("modelo/colunas_usadas.pkl")

        # Formulário de entrada
        with st.form("form_previsao"):
            airline = st.selectbox("Companhia Aérea:", sorted(encoder.classes_.tolist()))
            distance = st.number_input("Distância (milhas):", min_value=50, max_value=5000, value=500)
            month = st.selectbox("Mês do Voo:", list(range(1, 13)))
            submitted = st.form_submit_button("Prever Atraso")

        if submitted:
            # Preparar dados para previsão
            dados = pd.DataFrame({
                "Airline": [airline],
                "Distance": [distance],
                "Month": [month]
            })

            # Codificação e normalização
            dados["Airline"] = encoder.transform(dados["Airline"])
            X_novo = dados[colunas_usadas]
            X_novo_scaled = scaler.transform(X_novo)

            # Previsão
            predicao = modelo.predict(X_novo_scaled)
            resultado = "🔴 Atraso previsto" if predicao[0] == 1 else "🟢 Sem atraso previsto"
            st.success(f"Resultado da Previsão: {resultado}")