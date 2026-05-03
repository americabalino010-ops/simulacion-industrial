import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Industrial Digital Twin V11", layout="wide")
st.title("🏭 Planta 4.0: Simulación de Flujo y Costos")

# --- PANEL LATERAL: PARÁMETROS ---
st.sidebar.header("🕹️ Panel de Control")
total_piezas = st.sidebar.number_input("Lote de Producción", 5, 50, 10)

with st.sidebar.expander("⚙️ Estaciones de Trabajo"):
    t_corte = st.slider("Ciclo Corte (s)", 1.0, 10.0, 3.0)
    f_corte = st.slider("Fallo Corte (%)", 0, 15, 2)
    st.write("---")
    t_ens = st.slider("Ciclo Ensamble (s)", 1.0, 10.0, 4.0)
    f_ens = st.slider("Fallo Ensamble (%)", 0, 15, 5)

with st.sidebar.expander("💸 Parámetros de Costo"):
    costo_mat = st.sidebar.number_input("Materia Prima ($/pz)", 1.0, 100.0, 15.0)
    costo_min = st.sidebar.number_input("Costo Máquina ($/min)", 1.0, 50.0, 10.0)
    precio_v = st.sidebar.number_input("Precio de Venta ($/pz)", 10.0, 500.0, 60.0)

# --- FUNCIÓN DE RENDERIZADO 3D (EL LAYOUT) ---
def generar_planta_3d(pos_x, estado_pz, nombre_pz):
    fig = go.Figure()

    # 1. EL SUELO (Piso industrial)
    fig.add_trace(go.Mesh3d(
        x=[-5, 15, 15, -5], y=[-3, -3, 3, 3], z=[0, 0, 0, 0],
        color='lightslategray', opacity=0.4, showscale=False, name="Suelo"
    ))

    # 2. MÁQUINAS (Bloques 3D)
    # Estación Corte (Azul)
    fig.add_trace(go.Mesh3d(
        x=[-1, 1, 1, -1, -1, 1, 1, -1], y=[-1, -1, 1, 1, -1, -1, 1, 1], z=[0, 0, 0, 0, 2, 2, 2, 2],
        i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2], j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3], k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
        color='royalblue', opacity=0.9, name="CNC Corte"
    ))
    # Estación Ensamble (Naranja)
    fig.add_trace(go.Mesh3d(
        x=[9, 11, 11, 9, 9, 11, 11, 9], y=[-1, -1, 1, 1, -1, -1, 1, 1], z=[0, 0, 0, 0, 2, 2, 2, 2],
        i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2], j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3], k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
        color='orange', opacity=0.9, name="Ensamble"
    ))

    # 3. BANDA TRANSPORTADORA (Línea de flujo)
    fig.add_trace(go.Scatter3d(
        x=[0, 10], y=[0, 0], z=[0.1, 0.1],
        mode='lines', line=dict(color='black', width=12), name="Transportador"
    ))

    # 4. LA PIEZA (Esfera)
    col_map = {"PROCESO": "cyan", "OK": "lime", "RECHAZADA": "crimson"}
    fig.add_trace(go.Scatter3d(
        x=[pos_x], y=[0], z=[1],
        mode='markers+text', text=[nombre_pz], textposition="top center",
        marker=dict(size=12, color=col_map.get(estado_pz, "cyan"), symbol='diamond', line=dict(width=2, color='white'))
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-5, 15], title="Línea de Producción"),
            yaxis=dict(range=[-5, 5], visible=False),
            zaxis=dict(range=[0, 4], visible=False),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
        ),
        margin=dict(l=0, r=0, b=0, t=0), height=550
    )
    return fig

# --- LÓGICA DE SIMULACIÓN ---
if st.sidebar.button("▶️ Iniciar Producción"):
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        viz_p = st.empty()
        log_p = st.empty()
        
    with col_side:
        st.subheader("📈 Monitor de Calidad")
        m_yield = st.empty()
        m_cash = st.empty()
        st.markdown("---")
        st.subheader("📑 Reporte de Lote")
        tabla_p = st.empty()

    historial = []
    ganancia_t, perdida_t, scrap = 0, 0, 0

    for i in range(1, total_piezas + 1):
        nombre = f"P-{i}"
        
        # PASO 1: CORTE
        viz_p.plotly_chart(generar_planta_3d(0, "PROCESO", nombre), use_container_width=True)
        log_p.info(f"PROCESANDO: {nombre} en Estación de Corte")
        time.sleep(t_corte/2)
        err_c = np.random.random() < (f_corte/100)
        
        # PASO 2: ENSAMBLE (Si corte salió bien)
        if not err_c:
            viz_p.plotly_chart(generar_planta_3d(10, "PROCESO", nombre), use_container_width=True)
            log_p.warning(f"TRASLADO: {nombre} moviéndose a Ensamble")
            time.sleep(t_ens/2)
            err_e = np.random.random() < (f_ens/100)
        else:
            err_e = False

        # CÁLCULOS FINALES
        t_total = t_corte + t_ens + np.random.normal(0, 0.2)
        costo_run = (t_total/60) * costo_min
        
        if err_c or err_e:
            res = "RECHAZADA"
            perdida_t += (costo_mat + costo_run)
            scrap += 1
            pos_final = 0 if err_c else 10
        else:
            res = "OK"
            ganancia_t += (precio_v - (costo_mat + costo_run))
            pos_final = 10

        viz_p.plotly_chart(generar_planta_3d(pos_final, res, nombre), use_container_width=True)
        
        # ACTUALIZAR MÉTRICAS
        yield_val = ((i-scrap)/i)*100
        m_yield.metric("YIELD (Calidad)", f"{round(yield_val, 1)}%", f"{'-' if yield_val < 90 else ''}{scrap} fallos")
        m_cash.metric("UTILIDAD NETO", f"${round(ganancia_t - perdida_t, 2)}")
        
        historial.append({"ID": nombre, "Estado": res, "Tiempo Seg": round(t_total, 2)})
        tabla_p.dataframe(pd.DataFrame(historial).tail(5), use_container_width=True)
        time.sleep(0.5)

    st.success("✅ Turno terminado satisfactoriamente.")
    st.balloons()
