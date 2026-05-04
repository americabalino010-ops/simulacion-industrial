import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Industrial Blueprint V35", layout="wide")

# --- ESTILOS DE PLANO TÉCNICO ---
st.markdown("""
    <style>
    .stApp { background-color: #f3f4f6; }
    .blueprint-grid {
        background-color: #ffffff;
        border: 2px solid #374151;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 5px 5px 0px #374151;
    }
    .estacion-tecnica {
        background-color: #f9fafb;
        border: 2px solid #1e3a8a;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
    }
    .label-maquina {
        background-color: #1e3a8a;
        color: white;
        width: 100%;
        font-size: 12px;
        font-weight: bold;
        padding: 4px 0;
        position: absolute;
        top: 0;
    }
    .ingeniero-icon {
        font-size: 30px;
        position: absolute;
        bottom: 5px;
        right: 5px;
        filter: drop-shadow(2px 2px 2px rgba(0,0,0,0.3));
    }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DEL INGENIERO ---
if 'ing_x' not in st.session_state: st.session_state.ing_x = 2
if 'ing_y' not in st.session_state: st.session_state.ing_y = 2

# --- SIDEBAR: PANEL DE CONTROL ---
st.sidebar.title("🎮 Control de Planta")

# Mando Direccional para el Ingeniero
st.sidebar.write("### Desplazar Supervisor")
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
st.sidebar.subheader("🏗️ Diseño de Línea")
estaciones = ["Corte CNC", "Torno", "Prensa", "Ensamble", "Inspección"]
seleccion = st.sidebar.multiselect("Añadir Equipos:", estaciones, default=["Corte CNC", "Ensamble"])

config_plan = {}
for est in seleccion:
    with st.sidebar.expander(f"📍 Ubicación: {est}"):
        cx = st.selectbox(f"Col X - {est}", [1, 2, 3], index=seleccion.index(est) % 3)
        ry = st.selectbox(f"Fila Y - {est}", [1, 2, 3], index=seleccion.index(est) // 3)
        config_plan[est] = {"x": cx, "y": ry}

run = st.sidebar.button("▶️ INICIAR PRODUCCIÓN", use_container_width=True)

# --- PANTALLA PRINCIPAL: EL BLUEPRINT ---
st.title("🗺️ Plano Técnico: Gemelo Digital")

# Renderizado del Plano
grid_placeholders = {}

st.markdown('<div class="blueprint-grid">', unsafe_allow_html=True)
for r in [1, 2, 3]:
    cols = st.columns(3)
    for c in [1, 2, 3]:
        es_ing = (st.session_state.ing_x == c and st.session_state.ing_y == r)
        est_en_punto = [k for k, v in config_plan.items() if v['x'] == c and v['y'] == r]
        
        with cols[c-1]:
            html = "<div class='estacion-tecnica'>"
            if es_ing:
                html += "<div class='ingeniero-icon'>👷</div>"
            
            if est_en_punto:
                nombre = est_en_punto[0]
                html += f"<div class='label-maquina'>{nombre.upper()}</div>"
                # Iconografía según el tipo de máquina (basado en tu imagen)
                iconos = {"Corte CNC": "📠", "Torno": "🔩", "Prensa": "🏗️", "Ensamble": "🤖", "Inspección": "🔬"}
                html += f"<h1 style='margin-top:20px;'>{iconos.get(nombre, '⚙️')}</h1>"
                st.markdown(html + "</div>", unsafe_allow_html=True)
                grid_placeholders[nombre] = st.empty()
            else:
                html += "<small style='color:#ccc;'>ZONA LIBRE</small>"
                st.markdown(html + "</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- SIMULACIÓN ---
if run:
    status_bar = st.progress(0)
    for i in range(1, 6):
        for est in seleccion:
            grid_placeholders[est].info(f"📦 Procesando...")
            time.sleep(1)
            grid_placeholders[est].success("✅ OK")
            time.sleep(0.5)
            grid_placeholders[est].empty()
        status_bar.progress(i * 20)
    st.balloons()
