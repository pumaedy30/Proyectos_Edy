import streamlit as st
import math

# Título de la aplicación
st.title("Tabulador de Viáticos Foráneos")

# Generando listas de desición
eventos = ["Comida/Cena", "Cóctel", "Coffe/Break"]
decision = ["Si", "No"]

# Variables del usuario
tipo_evento = st.selectbox("Selecciona el tipo de evento:", eventos)
st.write(f"Evento seleccionado: {tipo_evento}.")
invitados = st.number_input(
    "Introduzca el número de invitados:",
    min_value=1,
    max_value=500,
    value=1,
    step=1
)
st.write(f"Número de invitados: {invitados}.")

distancia = st.number_input(
    "Distancia ida y vuelta (km):",
    min_value=0,
    value=1,
    step=1
)
st.write(f"Distancia ida y vuelta (km): {distancia}km.")

lleva_equipo = st.selectbox("¿Ambrosía lleva equipo?:", decision)
st.write(f"Ambrosía {lleva_equipo} lleva equipo.")

hay_pernocta = st.selectbox("¿Hay pernocta?:", decision)
if hay_pernocta == 'Si':
    noches = st.number_input("¿Cuántas noches?:",
    min_value=1,
    value=1,
    step=1
    )
    st.write(f"El equipo se queda {noches} noches.")
else:
    noches = 0
    st.write("No hay pernocta.")

# Diccionario para almacenar los datos del personal de servicio
personal_por_rango = [
    {
        "max_invitados": 50,
        "meseros": 5,
        "cocineros": 2,
        "capitanes": 1,
    },
    {
        "max_invitados": 100,
        "meseros": 10,
        "cocineros": 4,
        "capitanes": 1,
    },
    {
        "max_invitados": 200,
        "meseros": 20,
        "cocineros": 7,
        "capitanes": 2,
    },
    {
        "max_invitados": 350,
        "meseros": 35,
        "cocineros": 12,
        "capitanes": 3,
    },
    {
        "max_invitados": 500,
        "meseros": 50,
        "cocineros": 18,
        "capitanes": 4,
    },
]

# Diccionario para almacenar tarifas y costos de operaciones
tarifas = {
    "transporte": {
        "autobus": {
            "capacidad": 40,
            "renta": 20000,
            "caseta": 1200
        },
        "camioneta": {
            "capacidad": 18,
            "renta": 5000,
            "caseta": 600
        },
        "camion_carga": {
            "renta": 13000,
            "caseta": 1400,
            "combustible": {
                "rendimiento_km_litro": 4,
                "diesel_litro": 26,
                "sobrecosto": 0.20
            },
        }
    },


    "hospedaje": {
        "por_cuarto": 1800,
        "ocupacion_por_cuarto": 2
    },

    "operacion": {
        "alimentos_por_persona_dia": 350,
        "sobrecosto_foraneo_staff": 250,
        "buffer_imprevistos": 0.12,
        "minimo_invitados_camion_carga": 200
    }
}

# Asignando el personal
def total_personal(invitados):
    for regla in personal_por_rango:
        if invitados <= regla["max_invitados"]:
            return (
                regla["meseros"]
                + regla["cocineros"]
                + regla["capitanes"]
            )
    return 0
personal = total_personal(invitados)

# Calculando el sobrecosoto foráneo
def sobrecoto_foraneo(personal, tarifas):
    return personal * tarifas["operacion"]["sobrecosto_foraneo_staff"]

# Calculando el número de autobuses/camionetas
def transporte_personal(personal, tarifas):
    autobuses = personal // tarifas["transporte"]["autobus"]["capacidad"]
    restantes = personal % tarifas["transporte"]["autobus"]["capacidad"]

    camionetas = math.ceil(restantes / tarifas["transporte"]["camioneta"]["capacidad"])

    return autobuses, camionetas
autobuses, camionetas = transporte_personal(personal, tarifas)

# Calculando número de camiones de carga
def camion_carga(lleva_equipo, invitados, tarifas):
    if lleva_equipo == "Si":
        return max(1, invitados // tarifas["operacion"]["minimo_invitados_camion_carga"])
    return 0
camion_carga = camion_carga(lleva_equipo, invitados, tarifas)

# Calculando el costo de renta del transporte del personal
def costo_transporte_personal(autobuses, camionetas, tarifas):
    return (
        autobuses * tarifas["transporte"]["autobus"]["renta"]
        + camionetas * tarifas["transporte"]["camioneta"]["renta"]
    )

# Calculando el costo de renta de los camiones de carga
def costo_camiones_carga(camion_carga, tarifas):
    return camion_carga * tarifas["transporte"]["camion_carga"]["renta"]

# Calculando el costo de la gasolina del camión de carga
def costo_gasolina(camion_carga, distancia, tarifas):
    litros = distancia / tarifas["transporte"]["camion_carga"]["combustible"]["rendimiento_km_litro"]
    return camion_carga * litros * tarifas["transporte"]["camion_carga"]["combustible"]["diesel_litro"] * (1 + tarifas["transporte"]["camion_carga"]["combustible"]["sobrecosto"])

# Calculando el costo de las casetas por el equipo contratado
def costo_casetas(autobuses, camionetas, camion_carga, tarifas):
    return (
        autobuses * tarifas["transporte"]["autobus"]["caseta"]
        + camionetas * tarifas["transporte"]["camioneta"]["caseta"]
        + camion_carga * tarifas["transporte"]["camion_carga"]["caseta"]
    )

# Calculando el costo de hospedaje en caso de haber pernocta
def costo_hospedaje(hay_pernocta, personal, noches, tarifas):
    if hay_pernocta == 'Si':
        return personal // tarifas["hospedaje"]["ocupacion_por_cuarto"]  * tarifas["hospedaje"]["por_cuarto"] * noches
    return 0

# Calculando el costo de los alimentos en caso de haber pernocta 
def costo_alimentos(hay_pernocta, personal, noches, tarifas):
    if hay_pernocta == 'Si':
        return personal * tarifas["operacion"]["alimentos_por_persona_dia"] * (noches + 1)
    return 0

# Función global para hacer el cálculo total de los viáticos
def total_viaticos(hay_pernocta, personal, noches, invitados, distancia, autobuses, camionetas, camion_carga, tarifas):

    sobrecosto_for = sobrecoto_foraneo(personal, tarifas)
    transporte = costo_transporte_personal(autobuses, camionetas, tarifas)
    carga = costo_camiones_carga(camion_carga, tarifas)
    gasolina = costo_gasolina(camion_carga, distancia, tarifas)
    casetas = costo_casetas(autobuses, camionetas, camion_carga, tarifas)
    hospedaje = costo_hospedaje(hay_pernocta, personal, noches, tarifas)
    alimentos = costo_alimentos(hay_pernocta, personal, noches, tarifas)
    subt_logistica = sobrecosto_for + transporte + carga + gasolina + casetas + alimentos + hospedaje

    buffer = subt_logistica * tarifas["operacion"]["buffer_imprevistos"]
    total_viatico = subt_logistica + buffer
    costoxinvitado = total_viatico / invitados

    return sobrecosto_for, transporte, carga, gasolina, casetas, hospedaje, alimentos, subt_logistica, buffer, total_viatico, costoxinvitado

# Obteniendo los distintos gastos dados los datos introducidos por el usuario
sobrecosto_foraneo, transporte, camion, gasolina, casetas, hospedaje, alimentos,  subt_logistica, buffer, total_viatico, costoxinvitado = total_viaticos(hay_pernocta, personal, noches, invitados, distancia, autobuses, camionetas, camion_carga, tarifas)

# Mostrando los resultados obtenidos
st.title("Desglose de Resultados")
st.write(f"Sobrecosoto foráneo: ${sobrecosto_foraneo:,.2f}")
st.write(f"Tranporte de personal: ${transporte:,.2f}")
st.write(f"Camión de carga: ${camion:,.2f}")
st.write(f"Gasolina: ${gasolina:,.2f}")
st.write(f"Casetas: ${casetas:,.2f}")
st.write(f"Hospedaje: ${hospedaje:,.2f}")
st.write(f"Alimentos: ${alimentos:,.2f}")
st.write(f"Subtotal de logística: ${subt_logistica:,.2f}")
st.write(f"Buffer de imprevistos: ${buffer:,.2f}")
st.write(f"TOTAL DEL VIÁTICO: ${total_viatico:,.2f}")
st.write(f"Costo por invitado: ${costoxinvitado:,.2f}")

