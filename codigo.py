import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Nexus Ops Center", layout="wide")

# --- ESTILOS NEÓN INDUSTRIAL (CSS) ---
st.markdown("""
    <style>
    @import url('https://googleapis.com');
    .main { background-color: #0b0e14; color: #e0e0e0; font-family: 'Orbitron', sans-serif; }
    .stApp { background: radial-gradient(circle, #1a1f2c 0%, #0b0e14 100%); }
    .kpi-card { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; border-top: 2px solid #00d4ff; box-shadow: 0 4px 15px rgba(0, 212, 255, 0.2); text-align: center; }
    .station-box { background: rgba(0, 212, 255, 0.1); border: 1px solid #00d4ff; border-radius: 10px; padding: 15px; min-height: 150px; text-align: center; }
    .neon-text { color: #00d4ff; text-shadow: 0 0 10px #00d4ff; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADOS DE NAVEGACIÓN ---
if 'faceta' not in st.session_state: st.session_state.faceta = 'inicio'

# --- FACETA 1: BIENVENIDA (MODERNA) ---
if st.session_state.faceta == 'inicio':
    st.markdown("<h1 style='text-align: center; color: #00d4ff;'>NEXUS INDUSTRIAL OS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>SISTEMA DE SIMULACIÓN DE GEMELO DIGITAL v23.0</p>", unsafe_allow_html=True)
    
    col_b1, col_b2, col_b3 = st.columns([1,2,1])
    with col_b2:
        st.info("💡 Este sistema utiliza algoritmos de costeo ABC y métricas OEE en tiempo real para optimizar la cadena de valor.")
        if st.button("ACCEDER AL PANEL DE CONFIGURACIÓN"):
            st.session_state.faceta = 'config'
            st.rerun()

# --- FACETA 2: CONFIGURACIÓN ---
elif st.session_state.faceta == 'config':
    st.markdown("<h2 class='neon-text'>⚙️ CONFIGURACIÓN DE SISTEMA</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.write("### 💵 Parámetros Financieros")
        c_mat = st.number_input("Costo Directo Material ($)", 10.0, 100.0, 25.0)
        c_op = st.number_input("Carga Operativa ($/s)", 0.1, 10.0, 1.2)
        v_final = st.number_input("Precio de Salida ($)", 50.0, 1000.0, 150.0)
    with c2:
        st.write("### ⚙️ Parámetros de Planta")
        n_pz = st.number_input("Lote de Producción", 5, 50, 10)
        v_maq = st.slider("Velocidad de Ciclo (s)", 1, 5, 2)
        risk = st.slider("Tolerancia de Fallo (%)", 0, 20, 5)

    if st.button("🚀 INICIALIZAR LÍNEA DE PRODUCCIÓN"):
        st.session_state.params = {"mat": c_mat, "op": c_op, "v": v_final, "n": n_pz, "vel": v_maq, "risk": risk}
        st.session_state.faceta = 'sim'
        st.rerun()

# --- FACETA 3: SIMULACIÓN (ESTILO DASHBOARD TESLA) ---
elif st.session_state.faceta == 'sim':
    p = st.session_state.params
    st.markdown("<h2 class='neon-text' style='text-align: center;'>📡 LIVE TELEMETRY FEED</h2>", unsafe_allow_html=True)
    
    # KPIs SUPERIORES
    k1, k2, k3 = st.columns(3)
    met_cash = k1.empty()
    met_oee = k2.empty()
    met_step = k3.empty()

    st.write("---")
    
    # LÍNEA DE PRODUCCIÓN VISUAL (ISOMÉTRICA)
    col_a, col_f, col_b, col_res = st.columns([2, 1, 2, 2])
    v_a = col_a.empty()
    v_f = col_f.empty()
    v_b = col_b.empty()
    v_r = col_res.empty()

    # Lógica
    cash, malas, historial = 0, 0, []

    for i in range(1, int(p['n']) + 1):
        sku = f"NXS-{i:03d}"
        c_pz = p['mat']
        
        # ETAPA A: CORTE (Blue Neon)
        v_a.markdown(f"<div class='station-box'><h3 style='color:#00d4ff;'>🗜️ CNC UNIT</h3><p>PROCESSING: {sku}</p></div>", unsafe_allow_html=True)
        v_b.markdown("<div class='station-box' style='opacity:0.3;'>🤖 ROBOT<br>IDLE</div>", unsafe_allow_html=True)
        time.sleep(p['vel'])
        c_pz += (p['vel'] * p['op'])

        # ANIMACIÓN DE FLUJO
        v_a.markdown("<div class='station-box'>🗜️ CNC UNIT<br>STANDBY</div>", unsafe_allow_html=True)
        for d in ["▹", "▸▹", "▸▸▹", "▸▸▸▹", "📦"]:
            v_f.markdown(f"<h1 style='text-align:center; color:#00d4ff;'>{d}</h1>", unsafe_allow_html=True)
            time.sleep(0.2)

        # ETAPA B: ENSAMBLE (Orange Neon)
        v_b.markdown(f"<div class='station-box' style='border-color:orange;'><h3 style='color:orange;'>🤖 ROBOT</h3><p>ASSEMBLING: {sku}</p></div>", unsafe_allow_html=True)
        time.sleep(p['vel'])
        c_pz += (p['vel'] * p['op'])

        # CALIDAD
        fail = (np.random.random() * 100) < p['risk']
        if fail:
            res, col_msg = "CRITICAL FAIL", "red"
            malas += 1
            util_pz = 0
            v_r.error("🚨 SENSOR: REJECTED")
        else:
            res, col_msg = "PASSED", "#00ff00"
            util_pz = p['v'] - c_pz
            cash += util_pz
            v_r.success("💎 SENSOR: QUALITY OK")

        # KPIS
        met_cash.metric("NET MARGIN (USD)", f"${round(cash, 2)}")
        met_oee.metric("SYSTEM OEE", f"{round(((i-malas)/i)*100, 1)}%")
        met_step.metric("BATCH PROGRESS", f"{i}/{int(p['n'])}")
        
        historial.append({"SKU": sku, "Status": res, "Unit_Margin": round(util_pz, 2)})
        time.sleep(0.5)

    st.balloons()
    
    # REPORTE Y REINICIO
    df = pd.DataFrame(historial)
    csv = df.to_csv(index=False).encode('utf-8')
    c_down, c_reset = st.columns(2)
    with c_down: st.download_button("📥 EXPORT SYSTEM LOG (CSV)", csv, "nexus_report.csv", "text/csv")
    with c_reset: 
        if st.button("🔄 RESET SYSTEM"): 
            st.session_state.faceta = 'inicio'
            st.rerun()
