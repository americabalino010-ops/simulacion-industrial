import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Factory Architect Pro", layout="wide")

# --- ESTILOS VISUALES (LAYOUT Y HUD) ---
st.markdown("""
    <style>
    @import url('https://googleapis.com');
    .stApp { background-color: #1a1c2c; color: #fff; font-family: 'VT323', monospace; }
    .blueprint-grid { background-color: #333; border: 4px solid #555; padding: 10px; }
    .tile { height: 120px; border: 1px solid #444; display: flex; align-items: center; justify-content: center; position: relative; }
    .hud-panel { background: rgba(0,0,0,0.7); border: 2px solid #00ff00; padding: 10px; border-radius: 5px; color: #00ff00; font-size: 20px; }
    .sprite { font-size: 45px; filter: drop-shadow(2px 2px 0px #000); }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE DEL JUEGO (Session State) ---
if 'fase' not in st.session_state: st.session_state.fase = "planificacion"
if 'money' not in st.session_state: st.session_state.money = 1000 # Capital inicial

# --- FACETA 1: PLANIFICACIÓN (DISEÑO DEL LAYOUT) ---
if st.session_state.fase == "planificacion":
    st.title("🏗️ MODO DISEÑO: CONFIGURA TU PLANTA")
    
    st.sidebar.header("🛠️ Herramientas de Construcción")
    seleccion = st.sidebar.multiselect("Máquinas a instalar:", ["Corte", "Ensamble", "Calidad"], default=["Corte", "Ensamble"])
    
    config_plant = {}
    for m in seleccion:
        with st.sidebar.expander(f"⚙️ Configurar {m}"):
            mx = st.selectbox(f"Col X - {m}", [1, 2, 3], index=seleccion.index(m)%3)
            my = st.selectbox(f"Fila Y - {m}", [1, 2, 3], index=0)
            t_ciclo = st.slider(f"Velocidad {m}", 1, 5, 2)
            config_plant[m] = {"x": mx, "y": my, "t": t_ciclo}

    st.sidebar.markdown("---")
    lote = st.sidebar.number_input("Lote de producción", 5, 20, 5)
    
    # Dibujar plano previo
    st.write("### Plano de Planta (Layout)")
    for r in range(1, 4):
        cols = st.columns(3)
        for c in range(1, 4):
            obj = [k for k, v in config_plant.items() if v['x'] == c and v['y'] == r]
            with cols[c-1]:
                if obj:
                    st.markdown(f"<div class='tile'><span class='sprite'>⚙️</span><br>{obj[0]}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='tile' style='opacity:0.2;'>[VACÍO]</div>", unsafe_allow_html=True)

    if st.sidebar.button("🚀 CONFIRMAR DISEÑO Y ARRANCAR"):
        st.session_state.config = {"lote": lote, "plant": config_plant, "costo_fijo": 25, "vta": 120}
        st.session_state.fase = "operacion"
        st.rerun()

# --- FACETA 2: OPERACIÓN (SIMULACIÓN Y CÁLCULOS) ---
elif st.session_state.fase == "operacion":
    conf = st.session_state.config
    st.title("🏭 MODO OPERACIÓN: MONITOR EN VIVO")
    
    # HUD DE DATOS
    h1, h2, h3 = st.columns(3)
    cash_hud = h1.empty()
    yield_hud = h2.empty()
    log_hud = h3.empty()

    # VIEWPORT DEL JUEGO
    grid_placeholders = {}
    for r in range(1, 4):
        cols = st.columns(3)
        for c in range(1, 4):
            # Identificar máquina en esta celda
            maquina = [k for k, v in conf['plant'].items() if v['x'] == c and v['y'] == r]
            with cols[c-1]:
                if maquina:
                    st.markdown(f"<div class='tile'><b>{maquina[0].upper()}</b></div>", unsafe_allow_html=True)
                    grid_placeholders[maquina[0]] = st.empty()
                else:
                    st.markdown("<div class='tile' style='opacity:0.1;'>.</div>", unsafe_allow_html=True)

    # Lógica de Ejecución (Ingeniero se mueve y calcula)
    buenas, fallos = 0, 0
    for i in range(1, conf['lote'] + 1):
        for nombre, c_est in conf['plant'].items():
            # 1. El ingeniero llega a la máquina
            grid_placeholders[nombre].markdown("<span class='sprite'>👷⚙️</span>", unsafe_allow_html=True)
            log_hud.markdown(f"<div class='hud-panel'>INGENIERO: Procesando {nombre}...</div>", unsafe_allow_html=True)
            time.sleep(c_est['t'])
            
            # 2. Se procesa y sale la pieza
            grid_placeholders[nombre].markdown("<span class='sprite'>📦</span>", unsafe_allow_html=True)
            time.sleep(0.5)
            grid_placeholders[nombre].empty()
        
        # 3. Resultado final y cálculo
        error = np.random.random() < 0.1
        if not error:
            buenas += 1
            st.session_state.money += (conf['vta'] - conf['costo_fijo'])
            log_hud.markdown(f"<div class='hud-panel' style='color:#00ff00;'>✅ ÉXITO: +${conf['vta']-conf['costo_fijo']}</div>", unsafe_allow_html=True)
        else:
            fallos += 1
            st.session_state.money -= conf['costo_fijo']
            log_hud.markdown(f"<div class='hud-panel' style='color:#ff0000;'>❌ FALLO: -${conf['costo_fijo']}</div>", unsafe_allow_html=True)
        
        # Actualizar HUD
        cash_hud.markdown(f"<div class='hud-panel'>CASH: ${st.session_state.money}</div>", unsafe_allow_html=True)
        yield_hud.markdown(f"<div class='hud-panel'>YIELD: {round((buenas/(i))*100,1)}%</div>", unsafe_allow_html=True)
        time.sleep(1)

    st.balloons()
    if st.button("🔄 REDISEÑAR PLANTA"):
        st.session_state.fase = "planificacion"
        st.rerun()
