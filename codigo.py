import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Pixel Factory V48", layout="wide")

# --- CSS: ESTÉTICA DE VIDEOJUEGO DE CONSTRUCCIÓN ---
st.markdown("""
    <style>
    @import url('https://googleapis.com');
    .stApp { background-color: #2c3e50; font-family: 'VT323', monospace; }
    
    /* El Tablero de Juego */
    .game-board {
        background-color: #7f8c8d;
        border: 4px solid #34495e;
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 5px;
        padding: 10px;
        border-radius: 10px;
    }
    
    .pixel-cell {
        height: 120px;
        background-color: #95a5a6;
        border: 1px solid #7f8c8d;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        position: relative;
    }

    /* Estilo de los Sprites */
    .sprite-img { width: 60px; height: 60px; image-rendering: pixelated; }
    .player-img { width: 50px; height: 50px; position: absolute; z-index: 10; image-rendering: pixelated; }

    /* HUD Neón */
    .hud-header {
        background: #000;
        color: #33ff33;
        padding: 15px;
        border: 2px solid #33ff33;
        border-radius: 5px;
        font-size: 25px;
        margin-bottom: 20px;
        box-shadow: 0 0 10px #33ff33;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DEL JUEGO ---
if 'px' not in st.session_state: st.session_state.px = 0
if 'py' not in st.session_state: st.session_state.py = 0
if 'machines' not in st.session_state: st.session_state.machines = {}
if 'cash' not in st.session_state: st.session_state.cash = 1000

# --- IMÁGENES PIXEL ART (SPRITES) ---
SPRITES = {
    "Ingeniero": "https://icons8.com",
    "Corte": "https://icons8.com",
    "Ensamble": "https://icons8.com",
    "Almacén": "https://icons8.com"
}

# --- SIDEBAR: DISEÑADOR Y CONTROLES ---
st.sidebar.title("🎮 GAME MENU")

# 1. DISEÑO DE LA LÍNEA
with st.sidebar.expander("🏗️ MODO CONSTRUCTOR"):
    tipo = st.selectbox("Máquina:", ["Corte", "Ensamble", "Almacén"])
    cx = st.slider("Posición X", 0, 3, 0)
    cy = st.slider("Posición Y", 0, 3, 0)
    if st.button("🔨 Instalar"):
        st.session_state.machines[(cx, cy)] = tipo
        st.session_state.cash -= 150

# 2. MOVIMIENTO (EL PAD)
st.sidebar.markdown("---")
st.sidebar.subheader("🕹️ MOVER SUPERVISOR")
c1, c2, c3 = st.sidebar.columns(3)
if c2.button("▲"): st.session_state.py = max(0, st.session_state.py - 1)
if c1.button("◀"): st.session_state.px = max(0, st.session_state.px - 1)
if c3.button("▶"): st.session_state.px = min(3, st.session_state.px + 1)
c4, c5, c6 = st.sidebar.columns(3)
if c5.button("▼"): st.session_state.py = min(3, st.session_state.py + 1)

# --- HUD SUPERIOR ---
st.markdown(f"""
    <div class="hud-header">
        💰 MONEY: ${st.session_state.cash} | 
        👷 POS: ({st.session_state.px}, {st.session_state.py}) | 
        STATUS: ONLINE
    </div>
""", unsafe_allow_html=True)

# --- RENDERIZADO DEL MAPA ---
for y in range(4):
    cols = st.columns(4)
    for x in range(4):
        with cols[x]:
            # Detectar qué hay en esta celda
            es_jugador = (st.session_state.px == x and st.session_state.py == y)
            maquina_tipo = st.session_state.machines.get((x, y), None)
            
            html_tile = '<div class="pixel-cell">'
            
            if maquina_tipo:
                html_tile += f'<img src="{SPRITES[maquina_tipo]}" class="sprite-img"><br><small>{maquina_tipo}</small>'
            
            if es_jugador:
                html_tile += f'<img src="{SPRITES["Ingeniero"]}" class="player-img">'
            
            html_tile += '</div>'
            st.markdown(html_tile, unsafe_allow_html=True)

# --- ACCIONES Y CÁLCULOS ---
current_pos = (st.session_state.px, st.session_state.py)
if current_pos in st.session_state.machines:
    st.info(f"📍 Sobre: {st.session_state.machines[current_pos]}")
    if st.button("⚡ OPERAR MÁQUINA"):
        with st.status("Procesando..."):
            time.sleep(1)
            ganancia = np.random.randint(50, 100)
            st.session_state.cash += ganancia
            st.success(f"PIEZA LISTA: +${ganancia}")
            st.rerun()

if st.sidebar.button("🚨 RESET GAME"):
    st.session_state.clear()
    st.rerun()
