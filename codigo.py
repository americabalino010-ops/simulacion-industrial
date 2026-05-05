import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Simulador de Ingeniería Industrial", layout="wide")

st.title("🏭 Centro de Monitoreo y Simulación de Procesos")
st.markdown("""
Esta herramienta permite diseñar una línea de producción, configurar parámetros de operación y 
analizar la rentabilidad mediante un modelo de **Costeo Basado en Actividades (ABC)**.
""")

# --- BARRA LATERAL: ENTRADA DE DATOS (INGENIERÍA) ---
st.sidebar.header("🛠️ Configuración de Planta")

with st.sidebar.expander("💰 Parámetros Económicos"):
    costo_material = st.number_input("Costo Materia Prima ($/pz)", 10.0, 200.0, 50.0)
    precio_venta = st.number_input("Precio de Venta ($/pz)", 50.0, 500.0, 150.0)
    costo_energia = st.slider("Costo de Energía ($/seg)", 0.5, 5.0, 1.5)

with st.sidebar.expander("📐 Diseño de Línea"):
    estaciones = st.multiselect(
        "Selecciona las estaciones en orden:",
        ["Corte CNC", "Torno", "Ensamble", "Pintura", "Inspección de Calidad"],
        default=["Corte CNC", "Ensamble", "Inspección de Calidad"]
    )
    tasa_fallo = st.slider("Probabilidad de Defecto (%)", 0, 20, 5)
    lote = st.number_input("Tamaño del Lote (unidades)", 5, 50, 10)

# --- LÓGICA DE SIMULACIÓN (CÁLCULOS FUNDAMENTADOS) ---
if st.button("🚀 EJECUTAR SIMULACIÓN DE PROCESO"):
    
    # 1. Simulación de datos
    tiempo_promedio_estacion = 3.5 # segundos
    tiempo_total_proceso = len(estaciones) * tiempo_promedio_estacion
    costo_operativo_total = tiempo_total_proceso * costo_energia
    
    unidades_ok = 0
    unidades_scrap = 0
    historial = []

    for i in range(1, lote + 1):
        es_buena = np.random.random() > (tasa_fallo / 100)
        costo_acumulado = costo_material + costo_operativo_total
        
        if es_buena:
            unidades_ok += 1
            utilidad = precio_venta - costo_acumulado
            estado = "OK"
        else:
            unidades_scrap += 1
            utilidad = -costo_acumulado # Pérdida total del valor invertido
            estado = "SCRAP"
            
        historial.append({
            "Unidad": i,
            "Estado": estado,
            "Costo Total ($)": round(costo_acumulado, 2),
            "Utilidad Neta ($)": round(utilidad, 2)
        })

    df = pd.DataFrame(historial)
    utilidad_total = df["Utilidad Neta ($)"].sum()
    oee_calidad = (unidades_ok / lote) * 100

    # --- VISUALIZACIÓN DE RESULTADOS ---
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Utilidad Total", f"${round(utilidad_total, 2)}", delta=f"{round(utilidad_total/lote, 2)} $/pz")
    c2.metric("OEE (Calidad)", f"{round(oee_calidad, 1)}%")
    c3.metric("Unidades Scrap", unidades_scrap)
    c4.metric("Lead Time (Seg)", round(tiempo_total_proceso, 1))

    # Gráfico de Flujo de la Planta (Layout)
    st.subheader("🧬 Diagrama de Flujo del Diseño Actual")
    flujo_visual = " ⮕ ".join([f"[{e}]" for e in estaciones]) + " ⮕ [Almacén]"
    st.success(flujo_visual)

    # Gráfico Financiero
    st.subheader("📊 Análisis de Rentabilidad Acumulada")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Unidad"], y=df["Utilidad Neta ($)"].cumsum(), 
                             mode='lines+markers', name='Utilidad Acumulada',
                             line=dict(color='#00ff00' if utilidad_total > 0 else '#ff0000')))
    fig.update_layout(xaxis_title="Unidades Producidas", yaxis_title="Dólares ($)")
    st.plotly_chart(fig, use_container_width=True)

    # Tabla de Datos
    st.subheader("📋 Registro de Producción (Log)")
    st.dataframe(df, use_container_width=True)

else:
    st.info("Configura los parámetros en el panel izquierdo y presiona el botón para iniciar la simulación.")
