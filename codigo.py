import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Industrial Digital Twin V13", layout="wide")

st.title("🏭 Planta Interactiva: Control de Supervisor")

# --- PANEL LATERAL ---
st.sidebar.header("🕹️ Controles de Planta")
# CONTROL MANUAL DEL INGENIERO
pos_supervisor = st.sidebar.slider("📍 Mover Ingeniero (Supervisor)", -5.0, 15.0, 5.0, help="Desplaza al avatar por la planta")

with st.sidebar.expander("⚙️ Configuración de Lote"):
    total_piezas = st.number_input("Cantidad de piezas", 5, 50, 10)
    t_corte = st.slider("Velocidad Corte (s)", 1.0, 5.0, 2.0)
    t_ensamble = st.slider("Velocidad Ensamble (s)", 1.0, 5.0, 3.0)
    prob_error = st.sidebar.slider("Riesgo de Fallo (%)", 0, 20, 5)

# --- FUNCIÓN DE RENDERIZADO CORREGIDA ---
def generar_escena(pos_pieza, pos_ing, estado_pz, id_pz):
    fig = go.Figure()

    # 1. ENTORNO (Piso y Líneas)
    fig.add_trace(go.Mesh3d(x=[-8, 18, 18, -8, -8, 18, 18, -8], 
                           y=[-4, -4, 4, 4, -4, -4, 4, 4], 
                           z=[0, 0, 0, 0, 0.1, 0.1, 0.1, 0.1], 
                           color='lightgrey', opacity=0.3))
    
    fig.add_trace(go.Scatter3d(x=[0, 10], y=[0, 0], z=[0.1, 0.1], 
                               mode='lines', line=dict(color='black', width=10), name="Banda"))

    # 2. MÁQUINAS (BLOQUES 3D)
    # Estación Corte (Azul)
    fig.add_trace(go.Mesh3d(
        x=[-1, 1, 1, -1, -1, 1, 1, -1], 
        y=[-1, -1, 1, 1, -1, -1, 1, 1], 
        z=[0, 0, 0, 0, 2, 2, 2, 2], 
        color='blue', name="CNC"
    ))
    # Estación Ensamble (Naranja)
    fig.add_trace(go.Mesh3d(
        x=[9, 11, 11, 9, 9, 11, 11, 9], 
        y=[-1, -1, 1, 1, -1, -1, 1, 1], 
        z=[0, 0, 0, 0, 2, 2, 2, 2], 
        color='orange', name="Robot"
    ))

    # 3. LA PIEZA
    col_pz = "cyan" if estado_pz == "PROCESO" else ("green" if estado_pz == "OK" else "red")
    fig.add_trace(go.Scatter3d(
        x=[pos_pieza], y=[0], z=[0.6], mode='markers+text',
        text=[id_pz], textposition="top center",
        marker=dict(size=14, color=col_pz, symbol='diamond', line=dict(width=2, color='white'))
    ))

    # 4. EL INGENIERO (CONTROLADO POR EL USUARIO)
    fig.add_trace(go.Scatter3d(
        x=[pos_ing], y=[2.5], z=[1.5], 
        mode='markers+text', text=["👷 SUPERVISOR"],
        marker=dict(size=18, color='yellow', symbol='diamond', line=dict(width=3, color='black'))
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-8, 18], title="Eje X"), 
            yaxis=dict(range=[-5, 5], title="Eje Y"), 
            zaxis=dict(range=[0, 5], title="Eje Z"),
            aspectmode='manual', 
            aspectratio=dict(x=2.5, y=1, z=0.4)
        ),
        margin=dict(l=0, r=0, b=0, t=0), height=600
    )
    return fig

# --- SIMULACIÓN ---
if st.sidebar.button("🚀 INICIAR SIMULACIÓN INTERACTIVA"):
    andon = st.empty()
    viz = st.empty()
    
    st.write("---")
    c1, c2, c3 = st.columns(3)
    k_neto = c1.empty()
    k_fail = c2.empty()
    k_yield = c3.empty()

    historial = []
    ganancia, perdida, fallos = 0, 0, 0

    for i in range(1, total_piezas + 1):
        nombre = f"PZ-{i}"
        
        # ETAPA: CORTE
        andon.info(f"📍 {nombre} en Estación de Corte")
        viz.plotly_chart(generar_escena(0, pos_supervisor, "PROCESO", nombre), use_container_width=True)
        time.sleep(t_corte/2)

        # ETAPA: TRASLADO
        for s in np.linspace(0, 10, 5):
            viz.plotly_chart(generar_escena(s, pos_supervisor, "PROCESO", nombre), use_container_width=True)
            time.sleep(0.1)

        # ETAPA: ENSAMBLE
        andon.warning(f"🔧 {nombre} en Estación de Ensamble")
        viz.plotly_chart(generar_escena(10, pos_supervisor, "PROCESO", nombre), use_container_width=True)
        time.sleep(t_ensamble/2)

        # RESULTADO (Lógica de Calidad)
        es_error = np.random.random() < (prob_error/100)
        t_ciclo = (t_corte + t_ensamble) + np.random.normal(0, 0.2)
        costo_op = (t_ciclo/60) * 15 

        if es_error:
            res = "RECHAZADA"
            perdida += (20 + costo_op)
            fallos += 1
        else:
            res = "OK"
            ganancia += (100 - (20 + costo_op))

        historial.append({"ID": nombre, "Estado": res, "Tiempo": round(t_ciclo, 2)})
        
        # Mostrar resultado final en la posición correspondiente
        pos_final = 10 if res == "OK" else 0
        viz.plotly_chart(generar_escena(pos_final, pos_supervisor, res, nombre), use_container_width=True)
        
        # Actualizar Métricas
        k_neto.metric("Balance ($)", f"${round(ganancia - perdida, 2)}")
        k_fail.metric("Scrap", f"${round(perdida, 2)}", delta_color="inverse")
        k_yield.metric("Yield (%)", f"{round(((i-fallos)/i)*100, 1)}%")
        
    st.balloons()
