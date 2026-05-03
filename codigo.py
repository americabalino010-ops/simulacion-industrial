import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión de Planta Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div.stButton > button:first-child { background-color: #007bff; color: white; width: 100%; }
    .stMetric { background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- PANEL LATERAL ---
st.sidebar.title("🎮 Panel de Operaciones")
pos_supervisor = st.sidebar.radio("📍 Supervisión Actual", ["Almacén", "Corte", "Ensamble", "Calidad"])

with st.sidebar.expander("🛠️ Parámetros de Ingeniería"):
    lote = st.number_input("Tamaño del Lote", 5, 100, 15)
    t_proceso = st.slider("Velocidad de Línea (s)", 0.5, 5.0, 1.0)
    prob_error = st.slider("Tasa de Fallo Máxima (%)", 0, 25, 5)

# --- CUERPO PRINCIPAL ---
st.title("🏭 Monitor de Producción en Tiempo Real")
st.info(f"👷 Supervisor ubicado en: **{pos_supervisor}**")

# Espacios para KPIs
k1, k2, k3, k4 = st.columns(4)
utilidad_val = k1.empty()
yield_val = k2.empty()
rechazo_val = k3.empty()
progreso_val = k4.empty()

st.write("---")
st.write("### 🧩 Estado de Estaciones")
# Definimos 3 columnas fijas para las estaciones
col_corte, col_ensamble, col_calidad = st.columns(3)

with col_corte:
    st.subheader("🗜️ Corte")
    status_corte = st.empty()

with col_ensamble:
    st.subheader("🤖 Ensamble")
    status_ensamble = st.empty()

with col_calidad:
    st.subheader("🔍 Calidad")
    status_calidad = st.empty()

# --- LÓGICA DE SIMULACIÓN ---
if st.sidebar.button("▶️ INICIAR PRODUCCIÓN"):
    historial = []
    dinero, scrap, fallos = 0, 0, 0
    progreso_bar = st.progress(0)
    
    for i in range(1, lote + 1):
        sku = f"SKU-{200 + i}"
        
        # FASE 1: CORTE
        status_corte.warning(f"Procesando: {sku}")
        status_ensamble.write("Esperando...")
        status_calidad.write("---")
        time.sleep(t_proceso)
        
        # FASE 2: ENSAMBLE
        status_corte.success("Completado")
        status_ensamble.warning(f"Ensamblando: {sku}")
        time.sleep(t_proceso)
            
        # CONTROL DE CALIDAD
        status_ensamble.success("Completado")
        error = np.random.random() < (prob_error / 100)
        costo_fijo = 25
        
        if error:
            res = "RECHAZADO"
            scrap += costo_fijo
            fallos += 1
            status_calidad.error(f"❌ {sku}: DEFECTUOSA")
        else:
            res = "APROBADO"
            dinero += 75
            status_calidad.success(f"✅ {sku}: PASÓ")

        # Guardar historial
        historial.append({"SKU": sku, "Estado": res, "Ingreso": 75 if not error else 0, "Costo": costo_fijo if error else 0})
        
        # Actualizar Métricas
        utilidad_val.metric("Utilidad Neta", f"${dinero - scrap}")
        yield_val.metric("Calidad (Yield)", f"{round(((i-fallos)/i)*100, 1)}%")
        rechazo_val.metric("Pérdida (Scrap)", f"${scrap}")
        progreso_val.metric("Avance", f"{i}/{lote}")
        progreso_bar.progress(i / lote)
        
        time.sleep(0.5)

    # --- REPORTE FINAL ---
    st.balloons()
    st.write("---")
    st.write("### 📈 Análisis de Resultados")
    df = pd.DataFrame(historial)
    
    fig = px.bar(df, x="SKU", y=["Ingreso", "Costo"], 
                 title="Balance por Pieza",
                 color_discrete_map={"Ingreso": "#28a745", "Costo": "#dc3545"},
                 barmode="group")
    st.plotly_chart(fig, use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Reporte de Turno (CSV)", csv, "reporte_planta.csv", "text/csv")
