import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Pixel Factory V36", layout="wide")

# --- ESTILOS PIXEL ART (RETRO RPG) ---
st.markdown("""
    <style>
    /* Estilo general retro */
    .stApp { background-color: #2c3e50; }
    
    /* El "suelo" de baldosas de la fábrica */
    .pixel-grid {
        background-color: #95a5a6;
        border: 4px solid #34495e;
        padding: 5px;
        display: grid;
    }
    
    /* Cada baldosa/tile del mapa */
    .tile {
        background-color: #bdc3c7;
        border: 1px solid #7f8c8d;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
    }
    
    /* Personajes y máquinas con sombra de píxel */
    .sprite {
        font-size: 40px;
        filter: drop-shadow(2px 2px 0px #000);
    }
    
    .label-retro {
        background-color: #000;
        color: #33ff33; /* Verde terminal antigua */
        font-family: 'Courier New', Courier, monospace;
        font-size: 10px;
        padding: 2px 5px;
        border: 1px solid #33ff33;
        margin-top: 5px;
    }
    
    /* Estilo del menú de selección (como el de tu imagen) */
    .menu-retro {
        background-color: #2980b9;
        color: white;
        border: 3px solid white;
        padding: 10px;
        font-family: 'Courier New', Courier, monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DEL PERSONAJE ---
if 'px' not in st.session_state: st.session_state.px = 1
if 'py' not in st.session_state: st.session_state.py = 1

# --- PANEL DE CONTROL (RPG STYLE) ---
st.sidebar.title("🎮 COMMAND MENU")
st.sidebar.write(f"PLAYER POS: [{st.session_state.px},{st.session_state.py}]")

# Pad de movimiento
c1, c2, c3 = st.sidebar.columns(3)
if c2.button("▲"):
    if st.session_state.py > 1: st.session_state.py -= 1
c4, c5, c6 = st.sidebar.columns(3)
if c4.button("◀"):
    if st.session_state.px > 1: st.session_state.px -= 1
if c5.button("▼"):
    if st.session_state.py < 3: st.session_state.py += 1
if c6.button("▶"):
    if st.session_state.px < 3: st.session_state.px += 1

st.sidebar.markdown("---")
st.sidebar.subheader("🏗️ BUILDER")
maquinas = st.sidebar.multiselect("Añadir a la sala:", ["Computadora", "Laboratorio", "Banda", "Generador"], default=["Computadora", "Laboratorio"])

config_pixel = {}
for m in maquinas:
    with st.sidebar.expander(f"📍 Set {m}"):
        mx = st.selectbox(f"Col X - {m}",, index=maquinas.index(m)%3)
        my = st.selectbox(f"Fila Y - {m}",, index=maquinas.index(m)//3)
        config_pixel[m] = {"x": mx, "y": my}

run_sim = st.sidebar.button("▶️ START OPERATION")

# --- MAPA DE JUEGO (PIXEL GRID) ---
st.title("📟 Planta de Procesamiento 16-bit")

# Renderizado del mapa
st.markdown('<div class="pixel-grid">', unsafe_allow_html=True)
for r in:
    cols = st.columns(3)
    for c in:
        is_player = (st.session_state.px == c and st.session_state.py == r)
        obj_en_punto = [k for k, v in config_pixel.items() if v['x'] == c and v['y'] == r]
        
        with cols[c-1]:
            st.markdown('<div class="tile">', unsafe_allow_html=True)
            
            # Dibujar Objeto/Máquina
            if obj_en_punto:
                obj = obj_en_punto
                icons = {"Computadora": "🖥️", "Laboratorio": "🧪", "Banda": "⛓️", "Generador": "⚡"}
                st.markdown(f'<div class="sprite">{icons.get(obj, "📦")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="label-retro">{obj.upper()}</div>', unsafe_allow_html=True)
            
            # Dibujar Jugador encima o solo
            if is_player:
                st.markdown('<div class="sprite" style="position:absolute; top:10px;">🤵</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- LÓGICA DE SIMULACIÓN ---
if run_sim:
    st.markdown('<div class="menu-retro">SISTEMA INICIADO... PROCESANDO DATOS...</div>', unsafe_allow_html=True)
    progress = st.progress(0)
    for p in range(1, 101, 10):
        time.sleep(0.3)
        progress.progress(p)
    st.success("OPERACIÓN COMPLETADA CON ÉXITO")
