import streamlit as st
import pandas as pd
import numpy as np
import time

# --- INICIALIZACIÓN DE ESTADOS ---
if 'faceta' not in st.session_state:
    st.session_state.faceta = 'presentacion'

# --- FUNCIÓN PARA CAMBIAR DE FACETA ---
def cambiar_faceta(nombre_faceta):
    st.session_state.faceta = nombre_faceta

# --- FACETA 1: PRESENTACIÓN ---
if st.session_state.faceta == 'presentacion':
    st.title("🏭 Digital Twin: Simulador de Eficiencia Industrial")
    st.subheader("Bienvenido al Centro de Análisis de Producción")
    
    st.markdown("""
    Esta herramienta permite modelar una línea de producción real, analizando:
    * **Flujo de procesos** (Corte y Ensamble).
    * **Costeo Dinámico** (Material + Energía).
    * **Indicadores Globales** (OEE y Utilidad Neta).
    
    *Diseñado para la optimización de procesos y toma de decisiones financieras.*
    """)
    
    if st.button("🚀 Comenzar Configuración"):
        cambiar_faceta('parametros')

# --- FACETA 2: CONFIGURACIÓN DE PARÁMETROS ---
elif st.session_state.faceta == 'parametros':
    st.title("⚙️ Configuración del Modelo")
    st.write("Define los valores de entrada para tu simulación industrial.")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Variables de Costo")
        c_mat = st.number_input("Costo Materia Prima ($/pz)", 5.0, 100.0, 20.0)
        c_seg = st.number_input("Costo Energía/MO ($/seg)", 0.1, 10.0, 1.5)
        p_vta = st.number_input("Precio de Venta Final ($/pz)", 10.0, 500.0, 100.0)

    with col2:
        st.subheader("Variables de Operación")
        n_lote = st.number_input("Tamaño del Lote (unidades)", 5, 50, 10)
        t_ciclo = st.slider("Tiempo de Máquina (seg)", 1, 5, 2)
        fallo_p = st.slider("Tasa de Error Esperada (%)", 0, 30, 5)

    if st.button("▶️ Iniciar Simulación"):
        st.session_state.datos_sim = {
            "c_mat": c_mat, "c_seg": c_seg, "p_vta": p_vta,
            "n_lote": n_lote, "t_ciclo": t_ciclo, "fallo_p": fallo_p
        }
        cambiar_faceta('simulacion')
    
    if st.button("⬅️ Volver"):
        cambiar_faceta('presentacion')

# --- FACETA 3  ---
elif st.session_state.faceta == 'simulacion':
    d = st.session_state.datos_sim
    st.markdown(f"<h1 style='text-align: center; color: #00d4ff;'>🌐 Smart Factory Monitor</h1>", unsafe_allow_html=True)
    
    # Dashboard de KPIs estilo "Control Room"
    c1, c2, c3 = st.columns(3)
    met_util = c1.empty()
    met_oee = c2.empty()
    met_prog = c3.empty()

    # --- LAYOUT VISUAL DE PLANTA (Basado en tu imagen) ---
    st.write("---")
    # Usamos contenedores con bordes para simular las estaciones de tu imagen
    est_a, flow_1, est_b, flow_2, est_c = st.columns([2,1,2,1,2])
    
    with est_a:
        st.markdown("### 🖥️\n**CONTROL**")
        v_corte = st.empty()
    
    with est_b:
        st.markdown("### 🦾\n**ROBOT**")
        v_ensam = st.empty()
        
    with est_c:
        st.markdown("### 📦\n**SALIDA**")
        v_calidad = st.empty()

    v_flow = flow_1.empty() # Espacio para el movimiento
    log_eventos = st.empty()

    # --- LÓGICA DE MOVIMIENTO ---
    buenas, fallas, dinero = 0, 0, 0
    historial = []

    for i in range(1, int(d['n_lote']) + 1):
        sku = f"UNIT-{100+i}"
        costo_pz = d['c_mat']
        
        # 1. ESTACIÓN A: CORTE (Icono de proceso)
        v_corte.markdown(f"⚙️ **PROCESANDO**\n{sku}")
        time.sleep(d['t_ciclo'])
        costo_pz += (d['t_ciclo'] * d['c_seg'])
        
        # 2. MOVIMIENTO (Aquí simulamos el flujo de tu imagen)
        v_corte.markdown("✅ **LISTO**")
        for dot in [".", "..", "...", "📦"]:
            v_flow.markdown(f"<h2 style='text-align:center;'>{dot}</h2>", unsafe_allow_html=True)
            time.sleep(0.3)
        v_flow.empty()

        # 3. ESTACIÓN B: ENSAMBLE
        v_ensam.markdown(f"🔧 **ENSAMBLANDO**\n{sku}")
        time.sleep(d['t_ciclo'])
        costo_pz += (d['t_ciclo'] * d['c_seg'])
        v_ensam.markdown("✅ **LISTO**")

        # 4. CALIDAD Y RESULTADO
        error = (np.random.random() * 100) < d['fallo_p']
        if error:
            res = "RECHAZADA"
            fallas += 1
            ganancia_pz = 0
            v_calidad.error("💀 **FALLO**")
            log_eventos.error(f"⚠️ {sku}: Detectado defecto en sensor óptico.")
        else:
            res = "OK"
            buenas += 1
            ganancia_pz = d['p_vta'] - costo_pz
            dinero += ganancia_pz
            v_calidad.success("🌟 **PASS**")
            log_eventos.success(f"💎 {sku}: Calidad verificada. Listo para despacho.")

        # ACTUALIZAR MÉTRICAS
        met_util.metric("Utilidad Total", f"${round(dinero, 2)}")
        met_oee.metric("OEE (Calidad)", f"{round((buenas/i)*100, 1)}%")
        met_prog.metric("Lote", f"{i}/{int(d['n_lote'])}")
        
        time.sleep(0.8)

    st.balloons()
    # (Aquí iría el botón de descarga que ya tienes)

