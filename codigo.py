import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURACIÓN DE NIVEL PROFESIONAL ---
st.set_page_config(page_title="Industrial Digital Twin Pro", layout="wide")

# Estilo CSS para apariencia de Terminal de Datos
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { 
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
        border-left: 5px solid #1e3a8a;
    }
    .stButton>button {
        background-color: #1e3a8a;
        color: white;
        border-radius: 5px;
        height: 3em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Gemelo Digital: Optimización de Procesos V3.0")
st.caption("Módulo de Simulación Estocástica y Análisis de Rentabilidad ABC (Activity Based Costing)")

# --- SIDEBAR: CONFIGURACIÓN TÉCNICA ---
with st.sidebar:
    st.image("https://icons8.com", width=80)
    st.header("⚙️ Parámetros del Sistema")
    
    with st.expander("💰 Estructura de Costos", expanded=True):
        costo_material = st.number_input("Costo Unitario Material ($)", 10.0, 500.0, 45.0)
        precio_venta = st.number_input("Valor de Mercado ($)", 100.0, 1000.0, 180.0)
        costo_op_estacion = st.slider("Costo Operativo por Estación ($)", 5.0, 50.0, 12.5)
    
    with st.expander("📐 Configuración de Línea", expanded=True):
        estaciones = st.multiselect(
            "Layout de la Planta:",
            ["Corte CNC", "Torno Automático", "Ensamble Robótico", "Pintura", "Control de Calidad"],
            default=["Corte CNC", "Ensamble Robótico", "Control de Calidad"]
        )
        lote = st.slider("Tamaño del Lote (Batch)", 10, 500, 50)
        tasa_scrap = st.slider("Tasa de Defectos Esperada (%)", 0, 20, 5)

# --- MOTOR DE SIMULACIÓN ---
if st.button("🚀 INICIAR CORRIDA DE SIMULACIÓN", use_container_width=True):
    
    # Cálculo de Costo Absorbido (Ingeniería de Costos)
    costo_produccion_total = costo_material + (len(estaciones) * costo_op_estacion)
    
    resultados = []
    for i in range(1, lote + 1):
        # Modelo Estocástico de Calidad
        es_exito = np.random.random() > (tasa_scrap / 100)
        utilidad = (precio_venta - costo_produccion_total) if es_exito else -costo_produccion_total
        
        resultados.append({
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "SKU": f"PZ-{i:03}",
            "Status": "✅ Aceptado" if es_exito else "❌ Rechazado",
            "Costo Absorbido ($)": round(costo_produccion_total, 2),
            "Margen Neto ($)": round(utilidad, 2)
        })
    
    df = pd.DataFrame(resultados)
    ok = len(df[df["Status"] == "✅ Aceptado"])
    scrap_count = lote - ok
    utilidad_neta = df["Margen Neto ($)"].sum()
    oee = (ok / lote) * 100

    # --- DASHBOARD DE INDICADORES (KPIs) ---
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("EBITDA Total", f"${round(utilidad_neta, 2)}", delta=f"{round((utilidad_neta/lote),2)} $/pz")
    c2.metric("Throughput (OK)", f"{ok} pz")
    c3.metric("Scrap (Defectos)", f"{scrap_count} pz", delta=f"{round((scrap_count/lote)*100, 1)}%", delta_color="inverse")
    c4.metric("Lead Time Est.", f"{len(estaciones)*4.5} min")

    # --- VISUALIZACIÓN AVANZADA ---
    g1, g2 = st.columns([1, 2])
    
    with g1:
        # Velocímetro OEE (Estándar Industrial)
        fig_oee = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = oee,
            title = {'text': "Eficiencia (OEE) %"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#1e3a8a"},
                'steps' : [
                    {'range': [0, 70], 'color': "#ff4b4b"},
                    {'range': [70, 85], 'color': "#ffa500"},
                    {'range': [85, 100], 'color': "#2ecc71"}]
            }
        ))
        fig_oee.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_oee, use_container_width=True)

    with g2:
        # Curva de Rentabilidad Acumulada
        fig_cash = go.Figure()
        fig_cash.add_trace(go.Scatter(x=df.index, y=df["Margen Neto ($)"].cumsum(), 
                                      fill='tozeroy', name="Flujo de Caja",
                                      line=dict(color='#1e3a8a', width=3)))
        fig_cash.update_layout(title="Curva de Rentabilidad Acumulada", height=350, template="plotly_white")
        st.plotly_chart(fig_cash, use_container_width=True)

    # --- DIAGNÓSTICO E INGENIERÍA ---
    st.subheader("📝 Diagnóstico de Ingeniería")
    col_diag, col_break = st.columns([2, 1])

    with col_diag:
        if utilidad_neta > 0 and oee >= 85:
            st.success(f"**OPERACIÓN EXCELENTE.** La línea alcanza niveles de 'World Class Manufacturing'. El margen nulo es sostenible.")
        elif utilidad_neta > 0 and oee < 85:
            st.warning(f"**RENTABLE PERO INEFICIENTE.** El OEE de {round(oee,1)}% indica desperdicio oculto. Revise costos de no-calidad.")
        else:
            st.error(f"**CRISIS OPERATIVA.** La tasa de fallos anula el margen de contribución. Rediseñe el proceso.")

    with col_break:
        # Cálculo de Punto de Equilibrio
        margen_unitario = precio_venta - costo_material
        if margen_unitario > 0:
            costos_fijos_sim = len(estaciones) * costo_op_estacion
            break_even = costos_fijos_sim / (precio_venta - costo_produccion_total + 0.01)
            st.info(f"**Break-even:** {int(np.ceil(break_even))} unidades libres de defecto para ser rentable.")

    # --- REPORTES Y DESCARGAS ---
    st.divider()
    with st.expander("📋 Ver Trazabilidad Completa del Lote"):
        st.dataframe(df.style.background_gradient(subset=['Margen Neto ($)'], cmap='RdYlGn'), use_container_width=True)
    
    # Botón de Descarga
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Reporte Completo (CSV para Excel)",
        data=csv,
        file_name=f'Reporte_Industrial_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
        mime='text/csv',
        use_container_width=True
    )

else:
    st.info("👋 Bienvido. Configure los parámetros técnicos en el panel izquierdo y presione 'Iniciar' para simular.")
