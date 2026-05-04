import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Blueprint Designer V32", layout="wide")

# --- ESTILOS DE PLANTA ---
st.markdown("""
    <style>
    .grid-cell {
        border: 2px solid #dee2e6;
        border-radius: 12px;
        min-height: 140px;
        background-color: #ffffff;
        text-align: center;
        padding: 10px;
    }
    .kpi-card { background-color: #1e3a8a; color: white; padding: 10px; border-radius: 8px; text-align: center; }
    .ing-label { color: #f39c12; font-weight: bold; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# --- PANEL LATERAL: TOOLS ---
st.sidebar.title("🏗️ Factory Blueprint")

# 1. DISEÑO DEL PLANO
estaciones_disponibles = ["Corte", "Pulido", "Pintura", "Ensamble", "Calidad"]
seleccion = st.sidebar.multiselect("1. Elige Estaciones:", estaciones_disponibles, default=["Corte", "Ensamble"])

config_plan = {}
if seleccion:
    st.sidebar.markdown("---")
    st.sidebar.subheader("2. Ubicación de Máquinas")
    for est in seleccion:
        with st.sidebar.expander(f"📍 Posición: {est}"):
            # El usuario elige X e Y para cada máquina
            col_x = st.selectbox(f"Columna (X) - {est}", [1, 2, 3], index=seleccion.index(est) % 3)
            row_y = st.selectbox(f"Fila (Y) - {est}", [1, 2, 3], index=0)
            config_plan[est] = {"x": col_x, "y": row_y, "t": 2, "e": 5}

st.sidebar.markdown("---")
st.sidebar.subheader("👷 Control del Ingeniero")
# CONTROLES MANUALES PARA EL INGENIERO
ing_x = st.sidebar.slider("Desplazar Ingeniero (X)", 1, 3, 2)
ing_y = st.sidebar.slider("Desplazar Ingeniero (Y)", 1, 3, 2)

st.sidebar.markdown("---")
btn_run = st.sidebar.button("▶️ INICIAR PRODUCCIÓN", use_container_width=True)

# --- PANTALLA PRINCIPAL ---
st.title("🗺️ Centro de Mando: Layout Interactivo")

if not seleccion:
    st.info("👈 Diseña tu layout y coloca al ingeniero en el panel lateral.")
else:
    # Métricas
    k1, k2, k3 = st.columns(3)
    m_util = k1.empty()
    m_oee = k2.empty()
    m_ing = k3.empty()
    m_ing.markdown(f"<div class='kpi-card'>👷 POSICIÓN ING: ({ing_x}, {ing_y})</div>", unsafe_allow_html=True)

    # --- RENDERIZADO DEL MAPA (GRID 3x3) ---
    grid_placeholders = {}
    
    for r in [1, 2, 3]:
        cols = st.columns(3)
        for c in [1, 2, 3]:
            # Detectar si hay una máquina en este punto
            est_en_punto = [k for k, v in config_plan.items() if v['x'] == c and v['y'] == r]
            
            with cols[c-1]:
                # SI ESTÁ EL INGENIERO EN ESTA COORDENADA
                if ing_x == c and ing_y == r:
                    st.markdown("<div class='ing-label'>👷 SUPERVISOR AQUÍ</div>", unsafe_allow_html=True)
                
                if est_en_punto:
                    nombre = est_en_punto[0]
                    st.markdown(f"<div class='grid-cell'>⚙️<br><b>{nombre.upper()}</b><br><small>Coord: {c},{r}</small></div>", unsafe_allow_html=True)
                    grid_placeholders[nombre] = st.empty()
                else:
                    st.markdown("<div class='grid-cell' style='opacity:0.3; border-style:dashed;'><br>Zona Libre</div>", unsafe_allow_html=True)

    # --- LÓGICA DE PRODUCCIÓN ---
    if btn_run:
        buenas, dinero = 0, 0
        for i in range(1, 11): # Lote de 10 piezas
            sku = f"PZ-{i}"
            fail = False
            
            for est in seleccion:
                conf = config_plan[est]
                
                # LA PIEZA SE PROCESA
                grid_placeholders[est].info(f"📦 {sku}...")
                time.sleep(1.5)
                
                # CALIDAD
                if (np.random.random() * 100) < 5:
                    grid_placeholders[est].error("❌ RECHAZO")
                    fail = True
                    break
                else:
                    grid_placeholders[est].success("✅ OK")
                    time.sleep(0.5)
                    grid_placeholders[est].empty()

            if not fail:
                buenas += 1
                dinero += 100
            
            m_util.metric("Utilidad", f"${dinero}")
            m_oee.metric("OEE", f"{round((buenas/i)*100, 1)}%")
        
        st.balloons()
