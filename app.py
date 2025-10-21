import streamlit as st
import pandas as pd
import joblib
from keras.models import load_model

# ===== Завантаження моделі та скейлера =====
@st.cache_resource
def load_model_and_resources():
    model = load_model("boston_model.h5", compile=False)
    scaler = joblib.load("boston_scaler.pkl")
    return model, scaler

model, scaler = load_model_and_resources()

# ===== Завантаження даних =====
data = pd.read_excel("boston.xlsx")

# ===== Опис ознак =====
col_info = {
    "CRIM": "Рівень злочинності на душу населення",
    "ZN": "Розмір ділянки",
    "INDUS": "Щільність некоменрціних підприємств",
    "CHAS": "Чи проходить річка Charles через район (1 – так, 0 – ні)",
    "NOX": "Концентрація оксидів азоту (частин на 10 млн)",
    "RM": "Кількість кімнат у будинку",
    "AGE": "Вік будинку",
    "DIS": "Відстань до п’яти основних ділових центрів Бостона",
    "RAD": "Індекс доступу до радіальних шосе",
    "TAX": "Ставка податку на нерухомість",
    "PTRATIO": "Співвідношення учнів до вчителів у школах",
    "B": "Расовий показник",
    "LSTAT": "% населення з низьким соціальним статусом"
}

# ===== Заголовок =====
st.title("🏠 Boston Housing Price Prediction")
st.write("Введіть або скоригуйте параметри, щоб спрогнозувати **медіанну вартість житла** у тисячах доларів:")

# ===== Статистичні параметри =====
means = data.mean(numeric_only=True)
stds = data.std(numeric_only=True)

# ===== Введення користувача =====
user_input = {}

for col, desc in col_info.items():
    if col == "CHAS":
        # Радіокнопка
        chas_option = st.radio(
            f"{desc}",
            options=["Ні", "Так"],
            horizontal=True,
            index=int(means.get(col, 0))
        )
        user_input[col] = 1 if "Так" in chas_option else 0

    else:
        # Number input для всіх інших
        if col in ["RAD", "AGE", "RM"]:
            val = st.number_input(
                f"{desc}",
                min_value=0,
                value=int(means[col]),
                step=1
            )
        else:
            val = st.number_input(
                f"{desc}",
                min_value=0.0,
                value=float(means[col]),
                step=0.1
            )

        user_input[col] = val

        # Попередження, якщо значення надто відхиляється від середнього
        mean_val = means[col]
        std_val = stds[col]
        if std_val > 0 and abs(val - mean_val) > 3 * std_val:
            st.warning(
                f"⚠️ Значення для **{col}** ({desc}) суттєво відрізняється від середнього ({mean_val:.2f}). "
                "Можливо, це нереалістичне значення для реального району."
            )

# ===== Кнопка прогнозу =====
if st.button("🔮 Прогнозувати MEDV"):
    input_df = pd.DataFrame([user_input])

    # Масштабування
    input_scaled = scaler.transform(input_df)

    # Прогноз
    prediction = model.predict(input_scaled)
    medv = prediction[0][0]

    st.success(f"💰 Прогнозована медіанна вартість житла: **${medv * 1000:.2f}**")
    st.info("💡 Порада: змініть параметри, щоб побачити, як вони впливають на ціну житла.")
