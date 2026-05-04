import streamlit as st
import numpy as np
import time

# --- CONFIGURACIÓN DE PANTALLA ---
st.set_page_config(page_title="Industrial Pixel Arcade", layout="centered")

# --- ESTILO "RETRO ARCADE" (CSS) ---
st.markdown("""
    <style>
    @import url('https://googleapis.com');

    .stApp { background-color: #0d0d1a; }
    
    /* El marco de la pantalla del juego */
    .game-screen {
        border: 8px solid #3e3e3e;
        background-color: #1a1a2e;
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 0 20px #00d4ff;
    }

    /* Las baldosas del suelo */
    .tile {
        height: 100px;
        border: 1px solid #16213e;
        display: flex;
        justify-content: center;
        align-items: center;
        background-image: radial-gradient(#242444 1px, transparent 1px);
        background-size: 10px 10px;
    }

    /* Tipografía Retro */
    .retro-text {
        font-family: 'Press Start 2P', cursive;
        color: #00d4ff;
        font-size: 10px;
        text-align: center;
    }
    
    /* Animación de los sprites */
    .sprite { font-size: 40px; text-shadow: 2px 2px #000; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE MOVIMIENTO ---
if 'px' not in st.session_state: st.session_state.px = 0 # Eje X (0, 1, 2)
if 'py' not in st.session_state: st.session_state.py = 0 # Eje Y (0, 1, 2)

# --- PANEL DE CONTROL (JOYSTICK) ---
st.sidebar.markdown("<h2 class='retro-text'>CONTROLLER</h2>", unsafe_allow_html=True)
c1, c2, c3 = st.sidebar.columns(3)
if c2.button("▲"): st.session_state.py = max(0, st.session_state.py - 1)
c4, c5, c6 = st.sidebar.columns(3)
if c4.button("◀"): st.session_state.px = max(0, st.session_state.px - 1)
if c5.button("▼"): st.session_state.py = min(2, st.session_state.py + 1)
if c6.button("▶"): st.session_state.px = min(2, st.session_state.px + 1)

# --- DIBUJAR EL "NIVEL" (PLANTA) ---
st.markdown("<h1 class='retro-text' style='font-size:20px;'>FACTORY LEVEL 01</h1>", unsafe_allow_html=True)

# Aquí definimos dónde están las máquinas en el "mapa"
# (Fila, Columna): Tipo de máquina
maquinas = {
    (0, 0): {"icon": "⚙️", "name": "CORTE"},
    (0, 2): {"icon": "🦾", "name": "ROBOT"},
    (2, 2): {"icon": "🏭", "name": "OUT"}
}

def render_factory():
    with st.container():
        st.markdown('<div class="game-screen">', unsafe_allow_html=True)
        for r in range(3):
            cols = st.columns(3)
            for c in range(3):
                with cols[c]:
                    # ¿Está el jugador aquí?
                    player = "👷" if (st.session_state.px == c and st.session_state.py == r) else ""
                    # ¿Hay una máquina aquí?
                    obj = maquinas.get((r, c), {"icon": ""})["icon"]
                    
                    st.markdown(f"""
                        <div class="tile">
                            <span class="sprite">{obj}</span>
                            <span class="sprite" style="position:absolute;">{player}</span>
                        </div>
                    """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

render_factory()

# --- SIMULACIÓN ANIMADA (ESTO ES LO QUE DA FLUIDEZ) ---
if st.sidebar.button("▶ START MISSION"):
    status = st.empty()
    # Para que se vea fluido, movemos una "pieza" por el mapa
    # Definimos la ruta: (0,0) -> (0,1) -> (0,2) -> (1,2) -> (2,2)
    ruta = [(0,0), (0,1), (0,2), (1,2), (2,2)]
    
    for pos in ruta:
        status.markdown(f"<p class='retro-text'>MOVING OBJECT TO {pos}...</p>", unsafe_allow_html=True)
        # Aquí es donde ocurre la magia: 
        # En lugar de solo dibujar al final, dibujamos la pieza 📦 moviéndose
        # (Nota: Por limitaciones de Streamlit, aquí simulamos el flujo de datos)
        time.sleep(0.6)
    
    st.balloons()
    status.markdown("<p class='retro-text' style='color:#00ff00;'>MISSION COMPLETE!</p>", unsafe_allow_html=True)

