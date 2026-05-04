import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Simulador de Planta V24", layout="wide")

# --- ESTILO VISUAL (LAYOUT TIPO SIMIO) ---
st.markdown("""
    <style>
    .maquina { background-color: #f0f2f6; border: 2px solid #31333F; border-radius: 5px; padding: 10px; text-align: center; min-height: 100px; }
    .banda { background-color: #262730; color: white; height: 10px; margin: 20px 0; border-radius: 5px; }
    .gauge-label { font-size: 12px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

if 'faceta' not in st.session_state: st.session_state.faceta = 'inicio'

# --- FACETA 1: INICIO ---
if st.session_state.faceta == 'inicio':
    st.title("🏗️ Simulador Industrial Pro")
    st.write("Diseña y ejecuta modelos de producción basados en eventos discretos.")
    if st.button("Configurar Nuevo Modelo"):
        st.session_state.faceta = 'config'
        st.rerun()

# --- FACETA 2: CONFIGURACIÓN ---
elif st.session_state.faceta == 'config':
    st.subheader("🛠️ Parámetros de Simulación")
    c1, c2 = st.columns(2)
    with c1:
        n_lote = st.number_input("Piezas a procesar", 5, 50, 10)
        t_maq = st.slider("Velocidad de Máquina (s)", 1, 5, 2)
    with c2:
        costo_mat = st.number_input("Costo Material ($)", 10.0, 100.0, 25.0)
        precio_vta = st.number_input("Precio Venta ($)", 50.0, 500.0, 150.0)

    if st.button("▶️ Ejecutar Simulación"):
        st.session_state.p = {"n": n_lote, "t": t_maq, "c": costo_mat, "v": precio_vta}
        st.session_state.faceta = 'sim'
        st.rerun()

# --- FACETA 3: SIMULACIÓN (ESTILO SIMIO) ---
elif st.session_state.faceta == 'sim':
    p = st.session_state.p
    st.title("📈 Monitor de Planta en Ejecución")
    
    # KPIs Superiores
    k1, k2, k3 = st.columns(3)
    met_util = k1.empty()
    met_yield = k2.empty()
    met_prog = k3.empty()

    # --- DISEÑO DE PLANTA (Inspirado en la imagen) ---
    st.write("---")
    # Fila de Medidores (Gauges)
    g1, g2, g3 = st.columns(3)
    gauge_corte = g1.empty()
    gauge_ensam = g2.empty()
    gauge_calidad = g3.empty()

    # Fila de Máquinas y Bandas
    m_corte, b1, m_ensam, b2, m_almacen = st.columns([2, 3, 2, 3, 2])
    
    with m_corte: st.markdown('<div class="maquina">📦<br><b>GRANERO</b></div>', unsafe_allow_html=True)
    v_corte = m_corte.empty()
    
    v_b1 = b1.empty() # Banda transportadora 1
    
    with m_ensam: st.markdown('<div class="maquina">⚙️<br><b>PROCESO</b></div>', unsafe_allow_html=True)
    v_ensam = m_ensam.empty()
    
    v_b2 = b2.empty() # Banda transportadora 2
    
    with m_almacen: st.markdown('<div class="maquina">🏭<br><b>ALMACÉN</b></div>', unsafe_allow_html=True)
    v_almacen = m_almacen.empty()

    # Lógica de Ejecución
    buenas, dinero = 0, 0
    historial = []

    for i in range(1, int(p['n']) + 1):
        sku = f"PZ-{i}"
        
        # 1. EN CORTE (Gauges se mueven)
        gauge_corte.markdown(f"**Carga:** {'🟥' * 5} 100%")
        v_corte.warning(f"Procesando {sku}...")
        time.sleep(p['t'])
        gauge_corte.markdown(f"**Carga:** {'⬜' * 5} 0%")
        
        # 2. EN BANDA 1 (Animación de puntos)
        v_corte.write("Esperando...")
        for b in [".", "..", "...", "📦", "..."]:
            v_b1.markdown(f"<div class='banda' style='text-align:center;'>{b}</div>", unsafe_allow_html=True)
            time.sleep(0.3)
        v_b1.markdown('<div class="banda"></div>', unsafe_allow_html=True)

        # 3. EN ENSAMBLE
        gauge_ensam.markdown(f"**Carga:** {'🟧' * 5} 100%")
        v_ensam.warning(f"Ensamblando {sku}...")
        time.sleep(p['t'])
        gauge_ensam.markdown(f"**Carga:** {'⬜' * 5} 0%")

        # 4. CALIDAD Y RESULTADO FINAL
        v_ensam.write("Esperando...")
        error = np.random.random() < 0.1
        if not error:
            buenas += 1
            dinero += (p['v'] - p['c'])
            v_almacen.success(f"Recibido: {sku}")
            gauge_calidad.markdown(f"**Status:** ✅ OK")
        else:
            v_almacen.error(f"Rechazado: {sku}")
            gauge_calidad.markdown(f"**Status:** ❌ FAIL")

        # Actualizar KPIs
        met_util.metric("Utilidad Acumulada", f"${round(dinero, 2)}")
        met_yield.metric("Calidad (Yield)", f"{round((buenas/i)*100, 1)}%")
        met_prog.metric("Progreso", f"{i}/{int(p['n'])}")
        
        time.sleep(0.5)

    st.balloons()
    if st.button("Cerrar Turno y Reiniciar"):
        st.session_state.faceta = 'inicio'
        st.rerun()
