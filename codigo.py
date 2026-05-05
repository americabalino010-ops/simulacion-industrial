import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURACIÓN DE INTERFAZ PROFESIONAL ---
st.set_page_config(page_title="Industrial Logic V75", layout="wide", initial_sidebar_state="expanded")

# Estilo CSS para Dashboard de Alta Gama
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .main { background-color: #f1f3f6; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold; }
    .blueprint-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #d1d5db;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PANEL LATERAL (CONTROL DE ENTRADA) ---
with st.sidebar:
    st.title("🖥️ Centro de Control")
    st.divider()
    
    with st.expander("📝 Datos Maestros", expanded=True):
        costo_material = st.number_input("Costo Unitario Material ($)", 10.0, 500.0, 45.0)
        precio_venta = st.number_input("Valor de Mercado ($)", 100.0, 1000.0, 180.0)
        costo_labor = st.slider("Costo Labor/Energía ($/min)", 1.0, 10.0, 2.5)

    with st.expander("🏗️ Diseño del Proceso", expanded=True):
        estaciones = st.multiselect(
            "Configurar Layout:",
            ["Corte", "Torno", "Fresado", "Ensamble", "Pintura", "Calidad"],
            default=["Corte", "Ensamble", "Calidad"]
        )
        lote = st.number_input("Tamaño del Batch", 10, 1000, 50)
        eficiencia_base = st.slider("Tasa de Calidad Objetivo (%)", 80, 100, 95)

# --- ÁREA PRINCIPAL (DASHBOARD) ---
st.title("📊 Gemelo Digital: Optimización Operativa")

if st.button("▶️ EJECUTAR SIMULACIÓN DEL SISTEMA"):
    # --- CÁLCULOS DE INGENIERÍA FUNDAMENTADOS ---
    t_ciclo_promedio = 4.2 # Minutos por estación
    lead_time = len(estaciones) * t_ciclo_promedio
    costo_operativo = lead_time * costo_labor
    costo_total_unitario = costo_material + costo_operativo
    
    # Simulación Estocástica
    resultados = []
    for i in range(1, lote + 1):
        is_ok = np.random.random() < (eficiencia_base / 100)
        margen = (precio_venta - costo_total_unitario) if is_ok else -costo_total_unitario
        resultados.append({
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "SKU": f"PZ-{i:03}",
            "Calidad": "Aprobado" if is_ok else "Rechazado",
            "Costo ($)": round(costo_total_unitario, 2),
            "Utilidad ($)": round(margen, 2)
        })
    
    df = pd.DataFrame(resultados)
    ok_count = len(df[df["Calidad"] == "Aprobado"])
    scrap_count = lote - ok_count
    utilidad_neta = df["Utilidad ($)"].sum()
    oee = (ok_count / lote) * 100

    # --- FILA 1: KPIs CRÍTICOS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("EBITDA Operativo", f"${round(utilidad_neta, 2)}", delta=f"{round(utilidad_neta/lote, 2)} avg")
    c2.metric("OEE (Calidad)", f"{round(oee, 1)}%", delta=f"{round(oee-eficiencia_base,1)}% vs Obj")
    c3.metric("Throughput", f"{ok_count} pz")
    c4.metric("Cycle Time", f"{round(lead_time, 1)} min")

    # --- FILA 2: LAYOUT Y RENTABILIDAD ---
    col_layout, col_graph = st.columns([1, 1.5])

    with col_layout:
        st.markdown("<div class='blueprint-card'>", unsafe_allow_html=True)
        st.subheader("📍 Layout de Planta")
        # Visualización técnica del flujo
        pasos = ["IN"] + estaciones + ["WHS"]
        for idx in range(len(pasos)-1):
            st.code(f"{pasos[idx]} ➔ {pasos[idx+1]}")
        st.info(f"Costo Absorbido por Pieza: ${round(costo_total_unitario, 2)}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_graph:
        fig_cash = go.Figure()
        fig_cash.add_trace(go.Scatter(x=df.index, y=df["Utilidad ($)"].cumsum(), 
                                      fill='tozeroy', line=dict(color='#1e3a8a', width=3)))
        fig_cash.update_layout(title="Curva de Rentabilidad Acumulada", height=300, margin=dict(l=0,r=0,b=0,t=40))
        st.plotly_chart(fig_cash, use_container_width=True)

    # --- FILA 3: ANÁLISIS DE DATOS ---
    with st.expander("📋 Ver Registro de Producción Detallado y Exportar"):
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Reporte Completo (CSV)", data=csv, file_name="reporte_industrial.csv")

else:
    st.info("Utilice el panel lateral para configurar los parámetros y presione el botón de ejecución.")
