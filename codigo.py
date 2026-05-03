import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Industrial Digital Twin V9", layout="wide")
st.title("🏭 Simulador de Planta: Análisis de Costos y Calidad")

# --- PANEL LATERAL: CONFIGURACIÓN ---
st.sidebar.header("🛠️ Diseño de la Línea")
total_piezas = st.sidebar.number_input("Lote de Producción (piezas)", 5, 100, 10)

with st.sidebar.expander("Estación 1: CORTE"):
    t_corte = st.slider("Tiempo Ciclo (s)", 1.0, 10.0, 3.0)
    f_corte = st.slider("Tasa de Error Corte (%)", 0, 15, 2)

with st.sidebar.expander("Estación 2: ENSAMBLE"):
    t_ens = st.slider("Tiempo Ciclo (s) ", 1.0, 10.0, 4.0)
    f_ens = st.slider("Tasa de Error Ensamble (%)", 0, 15, 5)

st.sidebar.header("💰 Parámetros Financieros")
costo_material = st.sidebar.number_input("Costo Materia Prima ($/pz)", 1.0, 100.0, 15.0)
costo_minuto_maq = st.sidebar.number_input("Costo Operación ($/min)", 1.0, 50.0, 10.0)
precio_venta = st.sidebar.number_input("Precio de Venta ($/pz)", 10.0, 500.0, 60.0)

# --- INICIO DE SIMULACIÓN ---
if st.sidebar.button("🚀 Iniciar Producción"):
    col_viz, col_kpi = st.columns([2, 1])
    
    with col_viz:
        st.subheader("Vista de Planta 3D")
        placeholder_3d = st.empty()
    
    with col_kpi:
        st.subheader("Indicadores Financieros")
        kpi_ganancia = st.empty()
        kpi_perdida = st.empty()
        kpi_eficiencia = st.empty()
        st.write("---")
        tabla_log = st.empty()

    datos = []
    total_perdido = 0
    total_ganado = 0
    defectuosas = 0

    for i in range(1, total_piezas + 1):
        # Lógica Industrial: ¿Hubo error?
        error_corte = np.random.random() < (f_corte / 100)
        error_ens = np.random.random() < (f_ens / 100)
        
        t_real = (t_corte + t_ens) + np.random.normal(0, 0.2) # Variabilidad real
        costo_op = (t_real / 60) * costo_minuto_maq # Convertir seg a min para el costo
        
        if error_corte or error_ens:
            estado = "RECHAZADA"
            perdida_pz = costo_material + costo_op
            total_perdido += perdida_pz
            defectuosas += 1
            color_pz = "red"
        else:
            estado = "OK"
            ganancia_pz = precio_venta - (costo_material + costo_op)
            total_ganado += ganancia_pz
            color_pz = "green"

        datos.append({"ID": f"P-{i}", "Estado": estado, "T. Total": round(t_real, 2)})
        df_sim = pd.DataFrame(datos)

        # --- VISUALIZACIÓN 3D ---
        fig = go.Figure()
        # Estaciones fijas
        fig.add_trace(go.Scatter3d(x=[0, 5], y=[0, 0], z=[0, 0], mode='markers+text',
                     text=["CORTE", "ENSAMBLE"], marker=dict(size=15, symbol='square', color='gray')))
        # Piezas fluyendo
        fig.add_trace(go.Scatter3d(x=np.linspace(0, 5, len(df_sim)), y=np.random.normal(0, 0.1, len(df_sim)), 
                     z=df_sim["T. Total"]/5, mode='markers', 
                     marker=dict(size=8, color=['red' if e=="RECHAZADA" else 'green' for e in df_sim["Estado"]])))
        
        fig.update_layout(scene=dict(xaxis_title="Flujo", yaxis_title="Línea", zaxis_title="Tiempo"),
                          margin=dict(l=0, r=0, b=0, t=0), height=400)
        placeholder_3d.plotly_chart(fig, use_container_width=True)

        # --- ACTUALIZAR KPIS ---
        kpi_ganancia.metric("Utilidad Total (USD)", f"${round(total_ganado, 2)}", f"{round(total_ganado - total_perdido, 2)} neto")
        kpi_perdida.metric("Costo de No Calidad (Pérdida)", f"${round(total_perdido, 2)}", f"-{defectuosas} piezas", delta_color="inverse")
        kpi_eficiencia.metric("Yield (Calidad)", f"{round(((i-defectuosas)/i)*100, 1)}%")
        
        tabla_log.table(df_sim.tail(5))
        time.sleep(0.4)

    st.balloons()
    st.success(f"Simulación Finalizada. Balance Final: ${round(total_ganado - total_perdido, 2)}")

