import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Pixel Open World Factory", layout="centered")

# --- ESTILOS PIXEL ART (MUNDO ABIERTO) ---
st.markdown("""
    <style>
    @import url('https://googleapis.com');
    .stApp { background-color: #1a1a1a; font-family: 'VT323', monospace; }
    
    /* El suelo de la fábrica (Grid) */
    .factory-floor {
        background-color: #4e4e4e;
        border: 5px solid #222;
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 2px;
        width: 500px;
        margin: auto;
    }

    .tile {
        width: 95px;
        height: 95px;
        background-color: #757575;
        border: 1px solid #555;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }

    .hud-display {
        background-color: #000;
        border: 3px solid #00ff00;
        color: #00ff00;
        padding: 10px;
        font-size: 20px;
        border-radius: 5px;
        margin-bottom: 10px;
    }

    .sprite { font-size: 45px; z-index: 5; }
    .machine-sprite { font-size: 40px; opacity: 0.9; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DEL JUEGO (MEMORIA) ---
if 'player_x' not in st.session_state: st.session_state.player_x = 2
if 'player_y' not in st.session_state: st.session_state.player_y = 2
if 'machines' not in st.session_state: st.session_state.machines = {}
if 'cash' not in st.session_state: st.session_state.cash = 1000

# --- BARRA LATERAL: HERRAMIENTAS DE CONSTRUCCIÓN ---
st.sidebar.title("🛠️ MODO CONSTRUCTOR")
tipo_maquina = st.sidebar.selectbox("Elegir Maquinaria:", ["Corte ⚙️", "Ensamble 🦾", "Calidad 🔍"])
coord_x = st.sidebar.slider("Instalar en X", 0, 4, 0)
coord_y = st.sidebar.slider("Instalar en Y", 0, 4, 0)

if st.sidebar.button("🔨 Instalar Máquina"):
    st.session_state.machines[(coord_x, coord_y)] = tipo_maquina
    st.session_state.cash -= 200 # Costo de construcción

st.sidebar.markdown("---")
st.sidebar.subheader("🕹️ CONTROL DE MOVIMIENTO")
c1, c2, c3 = st.sidebar.columns(3)
if c2.button("▲"): st.session_state.player_y = max(0, st.session_state.player_y - 1)
if c1.button("◀"): st.session_state.player_x = max(0, st.session_state.player_x - 1)
if c3.button("▶"): st.session_state.player_x = min(4, st.session_state.player_x + 1)
c4, c5, c6 = st.sidebar.columns(3)
if c5.button("▼"): st.session_state.player_y = min(4, st.session_state.player_y + 1)

# --- HUD (DATOS FINANCIEROS) ---
st.markdown(f"<div class='hud-display'>CASH: ${st.session_state.cash} | POS: {st.session_state.player_x, st.session_state.player_y}</div>", unsafe_allow_html=True)

# --- RENDERIZADO DEL MAPA ABIERTO ---
with st.container():
    # Creamos el grid de 5x5
    for y in range(5):
        cols = st.columns(5)
        for x in range(5):
            with cols[x]:
                # Verificar si hay máquina aquí
                maquina_icon = st.session_state.machines.get((x, y), "")
                # Verificar si está el jugador
                es_jugador = (st.session_state.player_x == x and st.session_state.player_y == y)
                
                content = ""
                if es_jugador:
                    content += "<span class='sprite'>👷</span>"
                if maquina_icon:
                    content += f"<span class='machine-sprite'>{maquina_icon[-2:]}</span>"
                
                st.markdown(f"<div class='tile'>{content}</div>", unsafe_allow_html=True)

# --- INTERACCIÓN Y CÁLCULOS ---
current_pos = (st.session_state.player_x, st.session_state.player_y)
if current_pos in st.session_state.machines:
    st.warning(f"ESTÁS SOBRE: {st.session_state.machines[current_pos]}. ¡Presiona procesar para generar dinero!")
    if st.button("▶ PROCESAR PIEZA"):
        with st.spinner("Fabricando..."):
            time.sleep(1)
            ganancia = np.random.randint(50, 150)
            st.session_state.cash += ganancia
            st.success(f"¡Pieza completada! Ganancia: ${ganancia}")
            st.rerun()
