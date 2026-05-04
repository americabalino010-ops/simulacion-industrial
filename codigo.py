import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Industrial Pixel Factory", layout="wide")

# --- ESTILOS PIXEL ART INDUSTRIAL (V40) ---
st.markdown("""
    <style>
    .stApp { background-color: #1a1c2c; }
    
    /* Contenedor del Mapa */
    .factory-map {
        background-color: #5d6676; /* Color cemento industrial */
        border: 4px solid #333;
        padding: 0px;
        display: block;
    }
    
    /* Baldosas del suelo con efecto rejilla */
    .tile {
        background-color: #727b8a;
        border: 1px solid #5d6676;
        height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
    }
    
    /* La "Banda Transportadora" que conecta las celdas */
    .conveyor {
        position: absolute;
        width: 100%;
        height: 20px;
        background: repeating-linear-gradient(90deg, #333, #333 10px, #444 10px, #444 20px);
        bottom: 20px;
    }

    .sprite { font-size: 50px; filter: drop-shadow(3px 3px 0px rgba(0,0,0,0.4)); z-index: 2; }
    
    .machine-label {
        background-color: #000;
        color: #00ff00;
        font-family: 'monospace';
        font-size: 10px;
        padding: 2px 5px;
        border: 1px solid #00ff00;
        z-index: 3;
    }

    /* Diálogo estilo RPG (como el de tu imagen) */
    .rpg-dialog {
        background-color: #2980b9;
        color: white;
        border: 4px solid white;
        padding: 15px;
        font-family: 'monospace';
        border-radius: 5px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DEL JUGADOR ---
if 'px' not in st.session_state: st.session_state.px = 2
if 'py' not in st.session_state: st.session_state.py = 2

# --- BARRA LATERAL (COMMAND MENU) ---
st.sidebar.title("🕹️ COMMAND MENU")

# Pad Direccional
st.sidebar.write("### MOVER SUPERVISOR")
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
st.sidebar.subheader("🏗️ LINE DESIGNER")
# Estaciones Industriales Reales
estaciones = st.sidebar.multiselect("Añadir a la línea:", 
                                   ["Corte CNC", "Ensamble", "Calidad", "Almacén"], 
                                   default=["Corte CNC", "Ensamble", "Almacén"])

config_ind = {}
for est in estaciones:
    with st.sidebar.expander(f"📍 Ubicación: {est}"):
        ex = st.selectbox(f"Col X - {est}", [1, 2, 3], index=estaciones.index(est) % 3)
        ey = st.selectbox(f"Fila Y - {est}", [1, 2, 3], index=0)
        config_ind[est] = {"x": ex, "y": ey}

run = st.sidebar.button("▶️ START PRODUCTION")

# --- PANTALLA PRINCIPAL: MAPA INDUSTRIAL ---
st.title("🏭 Plant Floor: Operational View")

st.markdown('<div class="factory-map">', unsafe_allow_html=True)
for r in [1, 2, 3]:
    cols = st.columns(3)
    for c in [1, 2, 3]:
        is_player = (st.session_state.px == c and st.session_state.py == r)
        # Buscar qué máquina está en esta coordenada
        maquina_aqui = [k for k, v in config_ind.items() if v['x'] == c and v['y'] == r]
        
        with cols[c-1]:
            st.markdown('<div class="tile">', unsafe_allow_html=True)
            
            # Dibujar Banda Transportadora (decoración de fondo)
            st.markdown('<div class="conveyor"></div>', unsafe_allow_html=True)
            
            if maquina_aqui:
                m_name = maquina_aqui[0]
                # Sprites industriales
                icons = {"Corte CNC": "⚙️", "Ensamble": "🦾", "Calidad": "🔍", "Almacén": "🏭"}
                st.markdown(f'<div class="sprite">{icons.get(m_name, "📦")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="machine-label">{m_name.upper()}</div>', unsafe_allow_html=True)
            
            if is_player:
                # El supervisor aparece sobre la baldosa
                st.markdown('<div class="sprite" style="position:absolute; top:10px;">👷</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- SIMULACIÓN ---
if run:
    st.markdown(f"""
        <div class="rpg-dialog">
            <b>SISTEMA:</b> Iniciando lote de producción...<br>
            <b>SUPERVISOR:</b> Posicionado en ({st.session_state.px},{st.session_state.py}).<br>
            > Analizando eficiencia de la línea...
        </div>
    """, unsafe_allow_html=True)
    time.sleep(2)
    st.balloons()
