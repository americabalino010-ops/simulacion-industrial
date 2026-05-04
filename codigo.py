import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Industrial Tycoon V42", layout="wide")

# --- DISEÑO VISUAL DE VIDEOJUEGO (CSS) ---
st.markdown("""
    <style>
    @import url('https://googleapis.com');

    .stApp { background-color: #2e2e2e; }
    
    /* Pantalla de juego */
    .game-viewport {
        background-color: #4a4a4a; /* Suelo de metal */
        border: 6px solid #1a1a1a;
        padding: 0px;
        display: block;
        background-image: linear-gradient(#555 1px, transparent 1px), linear-gradient(90deg, #555 1px, transparent 1px);
        background-size: 50px 50px; /* Cuadrícula de construcción */
    }

    /* Baldosas de máquinas */
    .pixel-tile {
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border: 1px solid #333;
    }

    /* HUD de cálculos (Heads-Up Display) */
    .hud-panel {
        background-color: #2c3e50;
        border: 4px solid #ecf0f1;
        color: #f1c40f;
        padding: 15px;
        font-family: 'VT323', monospace;
        font-size: 22px;
        border-radius: 10px;
        box-shadow: 5px 5px 0px #000;
    }

    .sprite-img { font-size: 50px; filter: drop-shadow(4px 4px 0px #000); }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DEL JUEGO ---
if 'step' not in st.session_state: st.session_state.step = "setup"

# --- FACETA 1: MENÚ PRINCIPAL ---
if st.session_state.step == "setup":
    st.markdown("<h1 style='text-align:center; color:#f1c40f; font-family:VT323; font-size:60px;'>INDUSTRIAL TYCOON</h1>", unsafe_allow_html=True)
    
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("<div class='hud-panel'>🔧 AJUSTES DE PRODUCCIÓN<br>", unsafe_allow_html=True)
        lote = st.number_input("Lote de piezas", 5, 20, 5)
        t_ciclo = st.slider("Velocidad Maquinaria", 1, 4, 2)
    with col_r:
        st.markdown("<div class='hud-panel'>💰 AJUSTES FINANCIEROS<br>", unsafe_allow_html=True)
        costo = st.number_input("Costo Material", 10, 100, 25)
        precio = st.number_input("Precio Venta", 50, 500, 150)
    
    if st.button("▶️ START MISSION"):
        st.session_state.data = {"lote": lote, "t": t_ciclo, "costo": costo, "precio": precio}
        st.session_state.step = "game"
        st.rerun()

# --- FACETA 2: JUEGO Y CÁLCULOS ---
elif st.session_state.step == "game":
    d = st.session_state.data
    
    # HUD SUPERIOR (Cálculos en tiempo real)
    h1, h2, h3 = st.columns(3)
    cash_hud = h1.empty()
    yield_hud = h2.empty()
    status_hud = h3.empty()

    # VIEWPORT (El mapa de la fábrica)
    st.markdown('<div class="game-viewport">', unsafe_allow_html=True)
    row1 = st.columns(3)
    row2 = st.columns(3)
    row3 = st.columns(3)
    
    # Creamos un mapa de placeholders para animar
    placeholders = {
        (0,0): row1[0].empty(), (0,2): row1[2].empty(),
        (2,2): row3[2].empty()
    }
    
    # Dibujar decoraciones estáticas en el grid
    for c in [1]: row1[c].markdown('<div class="pixel-tile">⛓️</div>', unsafe_allow_html=True)
    for c in [0,1,2]: row2[c].markdown('<div class="pixel-tile"></div>', unsafe_allow_html=True)

    # Lógica de Simulación
    cash, buenas = 0, 0
    
    for i in range(1, d['lote'] + 1):
        sku = f"PZ-{i}"
        
        # 1. ESTACIÓN: CORTE
        placeholders[(0,0)].markdown('<div class="pixel-tile"><span class="sprite-img">👷⚙️</span><br>PROCESANDO...</div>', unsafe_allow_html=True)
        status_hud.markdown(f"<div class='hud-panel'>STATUS: {sku} IN CORTE</div>", unsafe_allow_html=True)
        time.sleep(d['t'])
        
        # 2. MOVIMIENTO (EL INGENIERO "CAMINA")
        placeholders[(0,0)].markdown('<div class="pixel-tile">⚙️</div>', unsafe_allow_html=True)
        status_hud.markdown(f"<div class='hud-panel'>STATUS: MOVING TO ASSEMBLY</div>", unsafe_allow_html=True)
        time.sleep(0.5)

        # 3. ESTACIÓN: ENSAMBLE
        placeholders[(0,2)].markdown('<div class="pixel-tile"><span class="sprite-img">👷🤖</span><br>ENSAMBLANDO...</div>', unsafe_allow_html=True)
        time.sleep(d['t'])
        
        # CÁLCULOS FINALES POR PIEZA
        error = np.random.random() < 0.1
        if not error:
            buenas += 1
            cash += (d['precio'] - d['costo'])
            res_icon = "📦✅"
        else:
            cash -= d['costo']
            res_icon = "🗑️❌"
            
        # 4. SALIDA
        placeholders[(0,2)].markdown('<div class="pixel-tile">🤖</div>', unsafe_allow_html=True)
        placeholders[(2,2)].markdown(f'<div class="pixel-tile"><span class="sprite-img">{res_icon}</span></div>', unsafe_allow_html=True)
        
        # ACTUALIZAR HUD
        cash_hud.markdown(f"<div class='hud-panel'>CASH: ${round(cash,2)}</div>", unsafe_allow_html=True)
        yield_hud.markdown(f"<div class='hud-panel'>YIELD: {round((buenas/i)*100,1)}%</div>", unsafe_allow_html=True)
        
        time.sleep(1)
        placeholders[(2,2)].empty()

    if st.button("🎮 RESTART"):
        st.session_state.step = "setup"
        st.rerun()
