import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Industrial Digital Twin V10", layout="wide")
st.title("🏭 Simulador de Planta: Animación de Flujo Real")

# --- PANEL LATERAL ---
st.sidebar.header("🛠️ Configuración de la Línea")
total_piezas = st.sidebar.number_input("Lote de Producción", 5, 50, 10)

col_c1, col_c2 = st.sidebar.columns(2)
with col_c1:
    t_corte = st.slider("Tiempo Corte (s)", 1.0, 10.0, 3.0)
with col_c2:
    f_corte = st.slider("Error Corte (%)", 0, 15, 2)

col_e1, col_e2 = st.sidebar.columns(2)
with col_e1:
    t_ens = st.slider("Tiempo Ensamble (s)", 1.0, 10.0, 4.0)
with col_e2:
    f_ens = st.slider("Error Ensamble (%)", 0, 15, 5)

st.sidebar.header("💰 Parámetros Financieros")
costo_material = st.sidebar.number_input("Costo Material ($/pz)", 1.0, 100.0, 15.0)
costo_min_maq = st.sidebar.number_input("Costo Máquina ($/min)", 1.0, 50.0, 10.0)
precio_venta = st.sidebar.number_input("Precio Venta ($/pz)", 10.0, 500.0, 60.0)

# --- FUNCIÓN PARA EL GRÁFICO DE PLANTA ---
def generar_planta(pos_x, estado_pieza, nombre_pieza):
    fig = go.Figure()
    # Dibujar Estaciones (Bases fijas)
    fig.add_trace(go.Scatter3d(
        x=[0, 10], y=[0, 0], z=[0, 0],
        mode='markers+text',
        text=["ESTACIÓN: CORTE", "ESTACIÓN: ENSAMBLE"],
        textposition="top center",
        marker=dict(size=30, symbol='square', color='lightgray', opacity=0.8),
        name="Maquinaria"
    ))
    # Dibujar la Pieza Actual en su posición
    color_map = {"PROCESO": "blue", "OK": "green", "RECHAZADA": "red"}
    fig.add_trace(go.Scatter3d(
        x=[pos_x], y=[0], z=[0.5],
        mode='markers+text',
        text=[nombre_pieza],
        textposition="top center",
        marker=dict(size=15, color=color_map.get(estado_pieza, "blue"), symbol='diamond'),
        name="Material"
    ))
    # Configuración de cámara y límites (para que no se mueva)
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-2, 12], title="Línea de Producción"),
            yaxis=dict(range=[-2, 2], visible=False),
            zaxis=dict(range=[0, 2], visible=False),
            aspectmode='manual',
            aspectratio=dict(x=2, y=0.5, z=0.3)
        ),
        margin=dict(l=0, r=0, b=0, t=0), height=500
    )
    return fig

# --- EJECUCIÓN ---
if st.sidebar.button("🚀 Iniciar Turno"):
    col_viz, col_kpi = st.columns([2, 1])
    with col_viz:
        viz_placeholder = st.empty()
        status_msg = st.empty()
    with col_kpi:
        st.subheader("KPIs Financieros")
        k1, k2 = st.columns(2)
        utilidad_metrica = k1.empty()
        perdida_metrica = k2.empty()
        yield_metrica = st.empty()
        tabla_resumen = st.empty()

    historial = []
    t_ganado, t_perdido, defectuosas = 0, 0, 0

    for i in range(1, total_piezas + 1):
        nombre = f"P-{i}"
        
        # --- ETAPA 1: CORTE ---
        status_msg.info(f"⚙️ {nombre}: Entrando a CORTE...")
        viz_placeholder.plotly_chart(generar_planta(0, "PROCESO", nombre), use_container_width=True)
        time.sleep(t_corte/4) # Simulación visual rápida
        
        error_c = np.random.random() < (f_corte/100)
        
        # --- ETAPA 2: ENSAMBLE ---
        if not error_c:
            status_msg.warning(f"🔧 {nombre}: Pasando a ENSAMBLE...")
            viz_placeholder.plotly_chart(generar_planta(10, "PROCESO", nombre), use_container_width=True)
            time.sleep(t_ens/4)
            error_e = np.random.random() < (f_ens/100)
        else:
            error_e = False # No llegó a ensamble

        # --- RESULTADO FINAL DE LA PIEZA ---
        t_total = t_corte + t_ens + np.random.normal(0, 0.2)
        costo_op = (t_total/60) * costo_min_maq
        
        if error_c or error_e:
            res, col_p = "RECHAZADA", "red"
            perdida = costo_material + costo_op
            t_perdido += perdida
            defectuosas += 1
        else:
            res, col_p = "OK", "green"
            ganancia = precio_venta - (costo_material + costo_op)
            t_ganado += ganancia

        historial.append({"ID": nombre, "Estado": res, "Costo Op.": round(costo_op, 2)})
        
        # Actualizar Visualización con resultado final
        pos_final = 0 if error_c else 10
        viz_placeholder.plotly_chart(generar_planta(pos_final, res, nombre), use_container_width=True)
        
        # Actualizar KPIs
        utilidad_metrica.metric("Utilidad Bruta", f"${round(t_ganado, 2)}")
        perdida_metrica.metric("Pérdida (Scrap)", f"${round(t_perdido, 2)}", delta_color="inverse")
        yield_metrica.metric("Calidad (Yield)", f"{round(((i-defectuosas)/i)*100, 1)}%")
        tabla_resumen.dataframe(pd.DataFrame(historial).tail(5), use_container_width=True)
        
        time.sleep(0.5)

    st.balloons()
    st.success(f"Turno Finalizado. Balance Neto: ${round(t_ganado - t_perdido, 2)}")


