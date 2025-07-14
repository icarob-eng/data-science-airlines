import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os

os.makedirs("modelo", exist_ok=True)
df = pd.read_csv("data/dados_agrupamento.csv")

# Criar variável alvo: atraso na chegada > 5 minutos
df["Atraso"] = (df["ArrDelay"] > 5).astype(int)

# Selecionar features preditoras 
X = df[["Airline", "Distance", "Month"]].copy()
y = df["Atraso"]

# Codificar variável categórica
le = LabelEncoder()
X["Airline"] = le.fit_transform(X["Airline"])

# Escalar os dados
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split treino/teste
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.3, random_state=42, stratify=y
)

# Treinamento do modelo
clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
clf.fit(X_train, y_train)

# Avaliação do modelo 
y_pred = clf.predict(X_test)
print("\n📊 Relatório de Classificação:")
print(classification_report(y_test, y_pred))

# --- Salvar modelo e transformadores ---
joblib.dump(clf, "modelo/classificador_voos.pkl")
joblib.dump(scaler, "modelo/scaler_classificacao.pkl")
joblib.dump(le, "modelo/encoder_airline_classificacao.pkl")
joblib.dump(["Airline", "Distance", "Month"], "modelo/colunas_usadas.pkl")

print("\n✅ Modelo de classificação treinado e salvo com sucesso!")
