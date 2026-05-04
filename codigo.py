import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Factory Blueprint V34", layout="wide")

# --- ESTILOS DE PLANO TÉCNICO (VISTA SUPERIOR) ---
st.markdown("""
    <style>
    .grid-container {
        background-color: #e5e7eb; /* Color cemento/industrial */
        padding: 10px;
        border-radius: 5px;
    }
    .grid-cell {
        border: 2px solid #9ca3af;
        height: 160px;
        background-color: #ffffff;
        text-align: center;
        padding: 5px;
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .ing-badge {
        background-color: #f59e0b;
        color: white;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 10px;
        position: absolute;
        top: 5px;
        right: 5px;
    }
    .machine-title { color: #111827; font-weight: bold; font-size: 14px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DEL SISTEMA ---
if 'ing_x' not in st.session_state: st.session_state.ing_x = 2
if 'ing_y' not in st.session_state: st.session_state.ing_y = 2

# --- BARRA LATERAL: CONTROL PAD ---
st.sidebar.title("🕹️ Mando del Supervisor")
st.sidebar.write(f"Coordenadas: **({st.session_state.ing_x}, {st.session_state.ing_y})**")

# Pad Direccional
c1, c2, c3 = st.sidebar.columns(3)
if c2.button("▲"):
    if st.session_state.ing_y > 1: st.session_state.ing_y -= 1
c4, c5, c6 = st.sidebar.columns(3)
if c4.button("◀"):
    if st.session_state.ing_x > 1: st.session_state.ing_x -= 1
if c5.button("▼"):
    if st.session_state.ing_y < 3: st.session_state.ing_y += 1
if c6.button("▶"):
    if st.session_state.ing_x < 3: st.session_state.ing_x += 1

st.sidebar.markdown("---")
st.sidebar.subheader("📐 Configuración de Planta")
seleccion = st.sidebar.multiselect("Añadir Estaciones:", ["Corte", "Pulido", "Pintura", "Ensamble", "Calidad"], default=["Corte", "Ensamble"])

config_plan = {}
for est in seleccion:
    with st.sidebar.expander(f"📍 {est}"):
        col_x = st.selectbox(f"Col X - {est}", [1, 2, 3], index=seleccion.index(est) % 3)
        row_y = st.selectbox(f"Fila Y - {est}", [1, 2, 3], index=seleccion.index(est) // 3)
        config_plan[est] = {"x": col_x, "y": row_y}

run = st.sidebar.button("▶️ INICIAR PRODUCCIÓN", use_container_width=True)

# --- PANTALLA PRINCIPAL: VISTA DE PLANO ---
st.title("🗺️ Blueprint: Vista Superior de Planta")

# Renderizado del Plano (Grid 3x3)
grid_placeholders = {}

st.markdown('<div class="grid-container">', unsafe_allow_html=True)
for r in [1, 2, 3]:
    cols = st.columns(3)
    for c in [1, 2, 3]:
        es_ing = (st.session_state.ing_x == c and st.session_state.ing_y == r)
        est_en_punto = [k for k, v in config_plan.items() if v['x'] == c and v['y'] == r]
        
        with cols[c-1]:
            # HTML para la celda del plano
            content = f"<div class='grid-cell'>"
            if es_ing:
                content += "<div class='ing-badge'>👷 SUPERVISOR</div>"
            
            if est_en_punto:
                nombre = est_en_punto[0]
                content += f"<div class='machine-title'>⚙️ {nombre.upper()}</div>"
                st.markdown(content + "</div>", unsafe_allow_html=True)
                grid_placeholders[nombre] = st.empty() # Espacio para la animación de la pieza
            else:
                content += "<small style='color:#9ca3af;'>ZONA LIBRE</small>"
                st.markdown(content + "</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- LÓGICA DE PRODUCCIÓN ---
if run:
    k1, k2 = st.columns(2)
    m_util = k1.empty()
    m_oee = k2.empty()
    
    buenas = 0
    for i in range(1, 6):
        for est in seleccion:
            grid_placeholders[est].info(f"📦 Procesando...")
            time.sleep(1)
            grid_placeholders[est].success("✅ LISTO")
            time.sleep(0.5)
            grid_placeholders[est].empty()
        
        buenas += 1
        m_util.metric("Utilidad", f"${buenas * 100}")
        m_oee.metric("OEE", f"{round((buenas/i)*100, 1)}%")

    st.balloons()
