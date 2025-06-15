import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Configuração da página ---
st.set_page_config(page_title="Análise de Voos 2019", layout="wide")

# --- Cabeçalho ---
st.markdown("# Análise de Voos - Ano 2019")
st.markdown("Use o menu lateral para navegar entre os gráficos e análises.")

# --- Menu lateral ---
st.sidebar.title("Menu de Análises")
opcao = st.sidebar.radio("Selecione uma análise:", [
    "Visão Geral",
    "Gráficos"
])

# --- Carregar dados ---
data_dir = 'data'
csv_path = os.path.join(data_dir, 'reduced2019.csv')

@st.cache_data
def carregar_dados(path):
    df_raw = pd.read_csv(path, usecols=["Airline", "DepDelay", "ArrDelay", "Origin", "Dest"])
    df_raw.dropna(subset=["Airline"], inplace=True)
    return df_raw

if os.path.exists(csv_path):
    df = carregar_dados(csv_path)

    # --- Filtrar Top 10 companhias com mais voos ---
    #if "Airline" in df.columns:
        #df = df.dropna(subset=["Airline"])  # Remove registros com Airline nulo
        #top10_empresas = df['Airline'].value_counts().nlargest(10).index
        #df = df[df['Airline'].isin(top10_empresas)]

        # Limitar número de linhas para não exceder o limite de memória do Streamlit
        #if len(df) > 10000:
            #df = df.sample(10000, random_state=42)

    # --- Exibir visualizações conforme opção escolhida ---
    if opcao == "Visão Geral":
        st.subheader("Visão Geral do Dataset")
        st.dataframe(df.head(100))  # Mostra apenas as primeiras 100 linhas
        st.write(df.describe())

    elif opcao == "Gráficos":
        st.subheader("Atrasos Médios por Companhia Aérea")
        if "Airline" in df.columns and "DepDelay" in df.columns:
            medias = df.groupby("Airline")["DepDelay"].mean().sort_values()
            st.bar_chart(medias)
        else:
            st.warning("Colunas necessárias não estão presentes no dataset.")

        st.subheader("Rotas com Mais Voos")
        if "Origin" in df.columns and "Dest" in df.columns:
            df["Rota"] = df["Origin"] + " → " + df["Dest"]
            rotas = df["Rota"].value_counts().head(10)
            st.bar_chart(rotas)
        else:
            st.warning("Colunas de origem/destino não estão disponíveis.")

        st.subheader("Comparação de Empresas Aéreas")
        if "Airline" in df.columns:
            metrica = st.selectbox("Escolha a métrica:", ["DepDelay", "ArrDelay"])
            if metrica in df.columns:
                # Usar apenas outliers no boxplot para não pesar
                fig = px.box(df, x="Airline", y=metrica, points="outliers",
                             title=f"Distribuição de {metrica} por Companhia")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"A métrica '{metrica}' não está disponível no dataset.")
        else:
            st.warning("Coluna 'Airline' não está presente no dataset.")

else:
    st.error("Arquivo de dados 'reduced2019.csv' não encontrado.")
