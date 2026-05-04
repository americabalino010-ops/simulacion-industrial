import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Factory Pad V33", layout="wide")

# --- ESTILOS DE PLANTA ---
st.markdown("""
    <style>
    .grid-cell {
        border: 2px solid #dee2e6;
        border-radius: 12px;
        min-height: 150px;
        background-color: #ffffff;
        text-align: center;
        padding: 10px;
        transition: 0.3s;
    }
    .ing-cell { background-color: #fff9db !important; border: 2px solid #f39c12 !important; }
    .ing-icon { font-size: 30px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DEL INGENIERO (Para que no se resetee la posición) ---
if 'ing_x' not in st.session_state: st.session_state.ing_x = 2
if 'ing_y' not in st.session_state: st.session_state.ing_y = 2

# --- PANEL LATERAL: CONTROL PAD ---
st.sidebar.title("🕹️ Control de Supervisor")
st.sidebar.write(f"Posición Actual: **({st.session_state.ing_x}, {st.session_state.ing_y})**")

# Botones de movimiento (Pad Direccional)
col_l, col_u_d, col_r = st.sidebar.columns(3)

if col_u_d.button("▲"):
    if st.session_state.ing_y > 1: st.session_state.ing_y -= 1

col_l_btn, col_down, col_r_btn = st.sidebar.columns(3)
if col_l_btn.button("◀"):
    if st.session_state.ing_x > 1: st.session_state.ing_x -= 1
if col_down.button("▼"):
    if st.session_state.ing_y < 3: st.session_state.ing_y += 1
if col_r_btn.button("▶"):
    if st.session_state.ing_x < 3: st.session_state.ing_x += 1

st.sidebar.markdown("---")
# --- DISEÑO DE PLANTA ---
estaciones_disponibles = ["Corte", "Pulido", "Pintura", "Ensamble", "Calidad"]
seleccion = st.sidebar.multiselect("Configura Estaciones:", estaciones_disponibles, default=["Corte", "Ensamble"])

config_plan = {}
if seleccion:
    for est in seleccion:
        with st.sidebar.expander(f"📍 {est}"):
            col_x = st.selectbox(f"X - {est}", [1, 2, 3], index=seleccion.index(est) % 3)
            row_y = st.selectbox(f"Y - {est}", [1, 2, 3], index=0)
            config_plan[est] = {"x": col_x, "y": row_y}

btn_run = st.sidebar.button("🚀 INICIAR SIMULACIÓN", use_container_width=True)

# --- PANTALLA PRINCIPAL ---
st.title("🗺️ Factory Blueprint: Control Interactivo")

# Renderizado del mapa
grid_placeholders = {}

for r in [1, 2, 3]:
    cols = st.columns(3)
    for c in [1, 2, 3]:
        # Detectar si el ingeniero está aquí
        es_ingeniero = (st.session_state.ing_x == c and st.session_state.ing_y == r)
        est_en_punto = [k for k, v in config_plan.items() if v['x'] == c and v['y'] == r]
        
        with cols[c-1]:
            clase_ing = "ing-cell" if es_ingeniero else ""
            html_cell = f"<div class='grid-cell {clase_ing}'>"
            
            if es_ingeniero:
                html_cell += "<div class='ing-icon'>👷</div>"
            
            if est_en_punto:
                nombre = est_en_punto[0]
                html_cell += f"⚙️<br><b>{nombre.upper()}</b><br><small>{c},{r}</small>"
                grid_placeholders[nombre] = st.empty()
            else:
                html_cell += f"<br><small style='color:gray;'>Zona {c},{r}</small>"
            
            html_cell += "</div>"
            st.markdown(html_cell, unsafe_allow_html=True)

# --- LÓGICA DE SIMULACIÓN ---
if btn_run:
    for i in range(1, 6): # Lote de 5 para probar
        for est in seleccion:
            grid_placeholders[est].info(f"📦 Procesando...")
            time.sleep(1)
            grid_placeholders[est].success("✅ OK")
            time.sleep(0.5)
            grid_placeholders[est].empty()
    st.balloons()
