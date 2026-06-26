import streamlit as st

# Título de la aplicación
st.title("Multiplicador de 5 números")

st.write("Introduce cinco números y presiona el botón para multiplicarlos.")

# Entradas
num1 = st.number_input("Número 1", value=1.0)
num2 = st.number_input("Número 2", value=1.0)
num3 = st.number_input("Número 3", value=1.0)
num4 = st.number_input("Número 4", value=1.0)
num5 = st.number_input("Número 5", value=1.0)

# Botón
if st.button("Multiplicar"):
    resultado = num1 * num2 * num3 * num4 * num5

    st.success(f"Resultado: {resultado}")