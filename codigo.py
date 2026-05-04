import streamlit as st
import numpy as np
import time

# --- CONFIGURACIÓN DE VIDEOJUEGO ---
st.set_page_config(page_title="Factory RPG V44", layout="wide")

# --- ESTILO VISUAL DE VIDEOJUEGO (CSS) ---
st.markdown("""
    <style>
    @import url('https://googleapis.com');
    
    .stApp { background-color: #1a1a1a; font-family: 'VT323', monospace; }
    
    /* Cuadro de diálogo estilo Pokémon/RPG */
    .dialog-box {
        background-color: #2980b9;
        border: 4px solid white;
        border-radius: 10px;
        padding: 20px;
        color: white;
        font-size: 24px;
        box-shadow: 0 0 0 4px #2980b9;
        margin-top: 20px;
        min-height: 100px;
    }
    
    /* Pantalla del juego */
    .viewport {
        background-color: #34495e;
        border: 8px solid #2c3e50;
        border-radius: 15px;
        height: 350px;
        display: flex;
        align-items: center;
        justify-content: space-around;
    }

    .stat-label { color: #f1c40f; font-size: 28px; text-shadow: 2px 2px #000; }
    .sprite { font-size: 60px; filter: drop-shadow(4px 4px 0px #000); }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE DEL JUEGO (Session State) ---
if 'step' not in st.session_state: st.session_state.step = "inicio"
if 'gold' not in st.session_state: st.session_state.gold = 0

# --- FACETA 1: PANTALLA DE TÍTULO ---
if st.session_state.step == "inicio":
    st.markdown("<h1 style='text-align:center; color:#f1c40f; font-size:70px;'>FACTORY TYCOON</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:white; font-size:30px;'>PRESIONA START PARA CONFIGURAR LA PLANTA</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("▶️ START GAME", use_container_width=True):
            st.session_state.step = "config"
            st.rerun()

# --- FACETA 2: CONFIGURACIÓN (MENÚ DE ITEMS) ---
elif st.session_state.step == "config":
    st.markdown("<h2 style='color:#3498db;'>🛠️ CONFIGURACIÓN DE MISIÓN</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    lote = c1.number_input("CANTIDAD DE PIEZAS", 5, 20, 5)
    precio = c2.number_input("PRECIO DE VENTA ($)", 50, 500, 150)
    
    st.session_state.config = {"lote": lote, "precio": precio, "costo": 40}
    
    if st.button("🚀 CONFIRMAR Y LANZAR"):
        st.session_state.step = "play"
        st.rerun()

# --- FACETA 3: EL JUEGO (SIMULACIÓN + DIÁLOGOS) ---
elif st.session_state.step == "play":
    conf = st.session_state.config
    
    # HUD (Marcador)
    h1, h2 = st.columns(2)
    h1.markdown(f"<p class='stat-label'>💰 ORO: ${st.session_state.gold}</p>", unsafe_allow_html=True)
    progreso_txt = h2.empty()

    # VIEWPORT (El mundo del juego)
    st.markdown('<div class="viewport">', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)
    v_corte = col_a.empty()
    v_trans = col_b.empty()
    v_ensam = col_c.empty()
    st.markdown('</div>', unsafe_allow_html=True)

    # Cuadro de Diálogo
    dialogo = st.empty()

    for i in range(1, conf['lote'] + 1):
        progreso_txt.markdown(f"<p class='stat-label'>PIEZA: {i}/{conf['lote']}</p>", unsafe_allow_html=True)
        
        # 1. INGENIERO EN CORTE
        v_corte.markdown("<div class='sprite'>👷⚙️</div>", unsafe_allow_html=True)
        dialogo.markdown("<div class='dialog-box'>INGENIERO: Iniciando corte de precisión... Esto nos costará $20 de energía.</div>", unsafe_allow_html=True)
        time.sleep(2)
        
        # 2. CAMINANDO
        v_corte.markdown("<div class='sprite'>⚙️</div>", unsafe_allow_html=True)
        v_trans.markdown("<div class='sprite'>🚶...📦</div>", unsafe_allow_html=True)
        dialogo.markdown("<div class='dialog-box'>INGENIERO: Llevando la pieza a la siguiente estación. ¡Cuidado con la banda!</div>", unsafe_allow_html=True)
        time.sleep(1)
        v_trans.empty()

        # 3. ENSAMBLE Y CÁLCULO
        v_ensam.markdown("<div class='sprite'>🤖👷</div>", unsafe_allow_html=True)
        dialogo.markdown("<div class='dialog-box'>INGENIERO: Ensamblando componentes finales... ¡Casi listo!</div>", unsafe_allow_html=True)
        time.sleep(2)

        # RESULTADO FINAL
        fallo = np.random.random() < 0.15
        if fallo:
            st.session_state.gold -= conf['costo']
            v_ensam.markdown("<div class='sprite'>🤖💥</div>", unsafe_allow_html=True)
            dialogo.markdown(f"<div class='dialog-box'>INGENIERO: ¡OH NO! La pieza SKU-{i} ha fallado el test. Perdimos ${conf['costo']} en materiales.</div>", unsafe_allow_html=True)
        else:
            ganancia = conf['precio'] - conf['costo']
            st.session_state.gold += ganancia
            v_ensam.markdown("<div class='sprite'>🤖✨</div>", unsafe_allow_html=True)
            dialogo.markdown(f"<div class='dialog-box'>INGENIERO: ¡Excelente! La pieza SKU-{i} es perfecta. Ganamos ${ganancia} netos.</div>", unsafe_allow_html=True)
        
        # Actualizar HUD
        h1.markdown(f"<p class='stat-label'>💰 ORO: ${st.session_state.gold}</p>", unsafe_allow_html=True)
        time.sleep(3)
        v_ensam.empty()

    st.balloons()
    if st.button("🔄 REINTENTAR MISIÓN"):
        st.session_state.step = "inicio"
        st.session_state.gold = 0
        st.rerun()
