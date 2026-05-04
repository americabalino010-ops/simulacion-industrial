import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Pixel Factory V36", layout="wide")

# --- ESTILOS PIXEL ART (RETRO RPG) ---
st.markdown("""
    <style>
    .stApp { background-color: #2c3e50; }
    .pixel-grid {
        background-color: #95a5a6;
        border: 4px solid #34495e;
        padding: 10px;
    }
    .tile {
        background-color: #bdc3c7;
        border: 1px solid #7f8c8d;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
    }
    .sprite {
        font-size: 45px;
        filter: drop-shadow(3px 3px 0px rgba(0,0,0,0.5));
    }
    .label-retro {
        background-color: #000;
        color: #33ff33;
        font-family: 'Courier New', monospace;
        font-size: 11px;
        padding: 2px 6px;
        border: 1px solid #33ff33;
        margin-top: 5px;
    }
    .menu-blue {
        background-color: #2980b9;
        color: white;
        border: 3px solid white;
        padding: 15px;
        font-family: 'Courier New', monospace;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DEL PERSONAJE ---
if 'px' not in st.session_state: st.session_state.px = 2
if 'py' not in st.session_state: st.session_state.py = 2

# --- PANEL DE CONTROL ---
st.sidebar.title("🕹️ COMMAND MENU")

# Pad de movimiento
st.sidebar.write("### MOVER SUPERVISOR")
c1, c2, c3 = st.sidebar.columns(3)
if c2.button("▲"):
    if st.session_state.py > 1: st.session_state.py -= 1
c4, c5, c6 = st.sidebar.columns(3)
if c4.button("◀"):
    if st.session_state.px > 1: st.session_state.px -= 1
if col_down := c5.button("▼"):
    if st.session_state.py < 3: st.session_state.py += 1
if c6.button("▶"):
    if st.session_state.px < 3: st.session_state.px += 1

st.sidebar.markdown("---")
st.sidebar.subheader("🏗️ BUILDER")
maquinas = st.sidebar.multiselect("Añadir a la sala:", 
                                  ["Computadora", "Laboratorio", "Banda", "Generador"], 
                                  default=["Computadora", "Laboratorio"])

config_pixel = {}
for m in maquinas:
    with st.sidebar.expander(f"Configurar {m}"):
        # AQUÍ ESTABA EL ERROR: Agregamos [1, 2, 3]
        mx = st.selectbox(f"Col X - {m}", [1, 2, 3], index=maquinas.index(m) % 3)
        my = st.selectbox(f"Fila Y - {m}", [1, 2, 3], index=0)
        config_pixel[m] = {"x": mx, "y": my}

run_sim = st.sidebar.button("▶️ START OPERATION")

# --- MAPA DE JUEGO ---
st.title("📟 Pixel Factory Monitor")

# Renderizado del mapa
st.markdown('<div class="pixel-grid">', unsafe_allow_html=True)
for r in [1, 2, 3]:
    cols = st.columns(3)
    for c in [1, 2, 3]:
        is_player = (st.session_state.px == c and st.session_state.py == r)
        # Buscar objeto en esta celda
        obj_en_punto = [k for k, v in config_pixel.items() if v['x'] == c and v['y'] == r]
        
        with cols[c-1]:
            st.markdown('<div class="tile">', unsafe_allow_html=True)
            
            # Dibujar Objeto
            if obj_en_punto:
                obj = obj_en_punto[0]
                icons = {"Computadora": "🖥️", "Laboratorio": "🧪", "Banda": "⛓️", "Generador": "⚡"}
                st.markdown(f'<div class="sprite">{icons.get(obj, "📦")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="label-retro">{obj.upper()}</div>', unsafe_allow_html=True)
            
            # Dibujar Jugador
            if is_player:
                st.markdown('<div class="sprite" style="position:absolute; top:20px; text-shadow: none;">🤵</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- SIMULACIÓN ---
if run_sim:
    st.markdown("""
        <div class="menu-blue">
            <b>SISTEMA NEXUS ONLINE</b><br>
            > Cargando protocolos de producción...<br>
            > Escaneando estaciones de trabajo...<br>
            > Operación en curso.
        </div>
    """, unsafe_allow_html=True)
    time.sleep(2)
    st.balloons()
    st.success("SIMULACIÓN FINALIZADA CON ÉXITO")
