import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Industrial Digital Twin V11", layout="wide")
st.title("🏭 Planta Industrial: Gemelo Digital de Producción")

# --- PANEL LATERAL ---
st.sidebar.header("🛠️ Ingeniería de Procesos")
total_piezas = st.sidebar.number_input("Lote a Producir", 5, 50, 10)

with st.sidebar.expander("Estación A: CORTE CNC"):
    t_corte = st.slider("Tiempo Ciclo (s)", 1.0, 10.0, 3.0, key="tc")
    f_corte = st.slider("Prob. Error (%)", 0, 15, 2, key="fc")

with st.sidebar.expander("Estación B: ENSAMBLE ROBÓTICO"):
    t_ens = st.slider("Tiempo Ciclo (s) ", 1.0, 10.0, 4.0, key="te")
    f_ens = st.slider("Prob. Error (%) ", 0, 15, 5, key="fe")

st.sidebar.header("💰 Costos de Manufactura")
costo_material = st.sidebar.number_input("Materia Prima ($/pz)", 1.0, 100.0, 20.0)
costo_min_maq = st.sidebar.number_input("Costo Energético ($/min)", 1.0, 50.0, 12.0)
precio_venta = st.sidebar.number_input("Valor de Mercado ($/pz)", 10.0, 500.0, 80.0)

# --- FUNCIÓN DE RENDERIZADO 3D (REALISMO) ---
def generar_planta_3d(pos_x, estado_pieza, nombre_pieza):
    fig = go.Figure()

    # 1. PISO DE LA FÁBRICA
    fig.add_trace(go.Mesh3d(
        x=[-5, 15, 15, -5, -5, 15, 15, -5],
        y=[-3, -3, 3, 3, -3, -3, 3, 3],
        z=[-0.2, -0.2, -0.2, -0.2, 0, 0, 0, 0],
        color='lightgrey', opacity=0.5, showscale=False, name="Suelo"
    ))

    # 2. MÁQUINA A (CORTE) - Cubo Azul
    fig.add_trace(go.Mesh3d(
        x=[-1, 1, 1, -1, -1, 1, 1, -1], y=[-1, -1, 1, 1, -1, -1, 1, 1], z=[0, 0, 0, 0, 2, 2, 2, 2],
        color='royalblue', opacity=0.9, name="CNC Corte"
    ))

    # 3. MÁQUINA B (ENSAMBLE) - Cubo Naranja
    fig.add_trace(go.Mesh3d(
        x=[9, 11, 11, 9, 9, 11, 11, 9], y=[-1, -1, 1, 1, -1, -1, 1, 1], z=[0, 0, 0, 0, 2, 2, 2, 2],
        color='orange', opacity=0.9, name="Ensamble"
    ))

    # 4. BANDA TRANSPORTADORA
    fig.add_trace(go.Scatter3d(
        x=[0, 10], y=[0, 0], z=[0.1, 0.1],
        mode='lines', line=dict(color='black', width=12), name="Transporte"
    ))

    # 5. PIEZA ACTUAL (Esfera)
    color_map = {"PROCESO": "cyan", "OK": "green", "RECHAZADA": "red"}
    fig.add_trace(go.Scatter3d(
        x=[pos_x], y=[0], z=[1],
        mode='markers+text', text=[nombre_pieza], textposition="top center",
        marker=dict(size=14, color=color_map.get(estado_pieza, "cyan"), 
                   symbol='circle', line=dict(width=2, color='white'))
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-5, 15], title="Layout (X)"),
            yaxis=dict(range=[-4, 4], title="Layout (Y)"),
            zaxis=dict(range=[0, 4], title="Altura (Z)"),
            aspectmode='manual', aspectratio=dict(x=2, y=1, z=0.4)
        ),
        margin=dict(l=0, r=0, b=0, t=0), height=500
    )
    return fig

# --- LÓGICA PRINCIPAL ---
if st.sidebar.button("🚀 ARRANCAR LÍNEA V11"):
    # Layout de la App
    col_viz, col_data = st.columns([2, 1])
    
    with col_viz:
        andon_placeholder = st.empty() # Semáforo Andon
        viz_placeholder = st.empty()
        status_txt = st.empty()
    
    with col_data:
        st.subheader("Métricas de Desempeño")
        m1 = st.empty() # Utilidad
        m2 = st.empty() # Pérdida
        m3 = st.empty() # Yield
        st.write("---")
        tabla_historial = st.empty()

    historial = []
    dinero_ganado, dinero_perdido, pz_malas = 0, 0, 0

    for i in range(1, total_piezas + 1):
        nombre = f"PZ-{i}"
        
        # --- ETAPA CORTE ---
        status_txt.info(f"⚡ {nombre}: Procesando en CNC Corte...")
        viz_placeholder.plotly_chart(generar_planta_3d(0, "PROCESO", nombre), use_container_width=True)
        time.sleep(t_corte/3)
        
        error_c = np.random.random() < (f_corte/100)
        
        # --- ETAPA ENSAMBLE ---
        if not error_c:
            status_txt.warning(f"🔧 {nombre}: Trasladando a Ensamble...")
            viz_placeholder.plotly_chart(generar_planta_3d(10, "PROCESO", nombre), use_container_width=True)
            time.sleep(t_ens/3)
            error_e = np.random.random() < (f_ens/100)
        else:
            error_e = False

        # --- CÁLCULOS INDUSTRIALES ---
        t_real = (t_corte + t_ens) + np.random.normal(0, 0.3)
        costo_op = (t_real/60) * costo_min_maq
        
        if error_c or error_e:
            res, col_res = "RECHAZADA", "red"
            dinero_perdido += (costo_material + costo_op)
            pz_malas += 1
        else:
            res, col_res = "OK", "green"
            dinero_ganado += (precio_venta - (costo_material + costo_op))

        historial.append({"Pieza": nombre, "Estado": res, "T.Ciclo": round(t_real, 2)})
        
        # --- ACTUALIZAR SEMÁFORO ANDON ---
        yield_actual = ((i - pz_malas) / i) * 100
        if yield_actual > 90:
            andon_placeholder.success("🟢 ESTADO: PRODUCCIÓN ÓPTIMA")
        elif yield_actual > 75:
            andon_placeholder.warning("🟡 ESTADO: REVISAR PARÁMETROS DE CALIDAD")
        else:
            andon_placeholder.error("🔴 ESTADO: LÍNEA DETENIDA POR EXCESO DE DEFECTOS")

        # --- REFRESCAR UI ---
        pos_fin = 0 if error_c else 10
        viz_placeholder.plotly_chart(generar_planta_3d(pos_fin, res, nombre), use_container_width=True)
        
        m1.metric("Utilidad Acumulada", f"${round(dinero_ganado, 2)}")
        m2.metric("Pérdida por Scrap", f"${round(dinero_perdido, 2)}", delta_color="inverse")
        m3.metric("Eficiencia (Yield)", f"{round(yield_actual, 1)}%")
        
        tabla_historial.dataframe(pd.DataFrame(historial).tail(5), use_container_width=True)
        time.sleep(0.3)

    st.balloons()
    balance = dinero_ganado - dinero_perdido
    st.subheader(f"📊 Reporte Final: Balance Neto de ${round(balance, 2)}")
