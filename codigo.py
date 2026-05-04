import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Industrial Designer V25", layout="wide")

# --- ESTILOS CSS (DISEÑO TIPO SIMIO) ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f4f9; }
    .estacion { 
        background-color: #ffffff; 
        border: 2px solid #2c3e50; 
        border-radius: 10px; 
        padding: 15px; 
        text-align: center; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .banda { 
        background-color: #34495e; 
        height: 12px; 
        margin-top: 50px; 
        border-radius: 5px; 
    }
    .gauge { font-size: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL: PANEL DE CONTROL (TOOLS) ---
st.sidebar.title("🛠️ Facility Tools")
st.sidebar.markdown("---")

# 1. Configuración de entrada
st.sidebar.subheader("📥 Input de Datos")
n_lote = st.sidebar.number_input("Cantidad de Piezas", 5, 50, 10)
t_proceso = st.sidebar.slider("Tiempo de Ciclo (s)", 0.5, 4.0, 1.5)

# 2. Configuración de costos
st.sidebar.subheader("💰 Parámetros Económicos")
costo_mat = st.sidebar.number_input("Costo Material ($)", 5.0, 50.0, 15.0)
precio_vta = st.sidebar.number_input("Precio Venta ($)", 20.0, 200.0, 80.0)

# 3. Probabilidades
st.sidebar.subheader("📉 Análisis de Riesgo")
prob_error = st.sidebar.slider("Tasa de Fallo (%)", 0, 25, 5)

st.sidebar.markdown("---")
iniciar = st.sidebar.button("▶️ RUN SIMULATION", use_container_width=True)
reiniciar = st.sidebar.button("🔄 RESET SYSTEM", use_container_width=True)

# --- PANTALLA PRINCIPAL: LIENZO DE SIMULACIÓN ---
st.title("🏭 Planta de Producción: Vista de Planta (Top-Down)")

if iniciar:
    # 1. KPIs Superiores (Dashboard de Control)
    k1, k2, k3, k4 = st.columns(4)
    met_util = k1.empty()
    met_yield = k2.empty()
    met_scrap = k3.empty()
    met_prog = k4.empty()

    st.write("---")

    # 2. Medidores de Aguja (Estilo Simio)
    st.write("📊 **Estado de Carga de Estaciones**")
    g1, g2, g3, g4, g5 = st.columns(5)
    gauge_a = g1.empty()
    gauge_b = g3.empty()
    gauge_c = g5.empty()

    # 3. Diseño de la Línea Física
    # Segmentamos el espacio: Estación -> Banda -> Estación -> Banda -> Salida
    m_a, b1, m_b, b2, m_c = st.columns([2, 3, 2, 3, 2])

    with m_a:
        st.markdown('<div class="estacion">⚙️<br><b>DESPULPADO</b></div>', unsafe_allow_html=True)
        v_a = st.empty()

    v_b1 = b1.empty() # Banda transportadora

    with m_b:
        st.markdown('<div class="estacion">🌀<br><b>MOLIENDA</b></div>', unsafe_allow_html=True)
        v_b = st.empty()

    v_b2 = b2.empty() # Banda transportadora

    with m_c:
        st.markdown('<div class="estacion">📦<br><b>ENSACADO</b></div>', unsafe_allow_html=True)
        v_c = st.empty()

    log_final = st.empty()

    # --- LÓGICA DE SIMULACIÓN ---
    buenas, fallas, dinero, scrap = 0, 0, 0, 0
    historial = []

    for i in range(1, n_lote + 1):
        sku = f"P-{i}"
        
        # FASE 1: DESPULPADO
        gauge_a.markdown("<p class='gauge'>🔴 100%</p>", unsafe_allow_html=True)
        v_a.info(f"Ocupado: {sku}")
        time.sleep(t_proceso)
        gauge_a.markdown("<p class='gauge'>⚪ 0%</p>", unsafe_allow_html=True)
        v_a.write("Libre")

        # TRÁNSITO 1 (Animación de la pieza por la banda)
        for d in [".", "..", "...", "📦", "...", "✔"]:
            v_b1.markdown(f"<div class='banda' style='text-align:center; color:white;'>{d}</div>", unsafe_allow_html=True)
            time.sleep(0.2)
        v_b1.markdown('<div class="banda"></div>', unsafe_allow_html=True)

        # FASE 2: MOLIENDA
        gauge_b.markdown("<p class='gauge'>🟠 100%</p>", unsafe_allow_html=True)
        v_b.warning(f"Ocupado: {sku}")
        time.sleep(t_proceso)
        gauge_b.markdown("<p class='gauge'>⚪ 0%</p>", unsafe_allow_html=True)
        v_b.write("Libre")

        # TRÁNSITO 2
        for d in [".", "..", "...", "📦", "...", "✔"]:
            v_b2.markdown(f"<div class='banda' style='text-align:center; color:white;'>{d}</div>", unsafe_allow_html=True)
            time.sleep(0.2)
        v_b2.markdown('<div class="banda"></div>', unsafe_allow_html=True)

        # FASE 3: CALIDAD / ENSACADO
        error = (np.random.random() * 100) < prob_error
        costo_total_pz = costo_mat + (t_proceso * 2 * 1.5) # Material + Energía en 2 máquinas
        
        if error:
            fallas += 1
            scrap += costo_total_pz
            v_c.error(f"❌ FALLO: {sku}")
            res = "RECHAZADA"
        else:
            buenas += 1
            ganancia = precio_vta - costo_total_pz
            dinero += ganancia
            v_c.success(f"✅ OK: {sku}")
            res = "OK"

        # ACTUALIZAR KPIs
        met_util.metric("Utilidad Neta", f"${round(dinero, 2)}")
        met_yield.metric("OEE (Calidad)", f"{round((buenas/i)*100, 1)}%")
        met_scrap.metric("Costo Scrap", f"${round(scrap, 2)}", delta_color="inverse")
        met_prog.metric("Avance", f"{i}/{n_lote}")

        historial.append({"SKU": sku, "Estado": res, "Margen": round(precio_vta - costo_total_pz if not error else -costo_total_pz, 2)})
        time.sleep(0.5)

    st.balloons()
    st.write("### 📝 Reporte Final de Turno")
    st.dataframe(pd.DataFrame(historial), use_container_width=True)

elif reiniciar:
    st.rerun()

else:
    st.info("👈 Configura los parámetros en el panel de herramientas y presiona 'RUN SIMULATION'")
