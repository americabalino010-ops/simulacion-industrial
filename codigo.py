import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Industrial Designer V26", layout="wide")

# --- ESTILOS CSS CORREGIDOS (COLORES Y CONTRASTE) ---
st.markdown("""
    <style>
    /* Fondo de la aplicación */
    .stApp { background-color: #f0f2f6; }
    
    /* Títulos principales en azul oscuro para que se vean bien */
    h1, h2, h3 { color: #1e3a8a !important; font-weight: bold; }
    
    /* Estilo de las cajas de las estaciones */
    .estacion { 
        background-color: #ffffff; 
        border: 3px solid #1e3a8a; 
        border-radius: 12px; 
        padding: 20px; 
        text-align: center; 
        box-shadow: 4px 4px 10px rgba(0,0,0,0.1);
        color: #111827; /* Texto negro dentro de la caja */
    }
    
    /* Banda transportadora oscura */
    .banda { 
        background-color: #374151; 
        height: 15px; 
        margin-top: 60px; 
        border-radius: 8px;
        border: 1px solid #111827;
    }
    
    /* Medidores (Gauges) con colores fuertes */
    .gauge { 
        font-size: 22px; 
        font-weight: bold; 
        color: #1e3a8a;
        margin-bottom: 5px;
    }
    
    /* Texto de métricas (KPIs) */
    [data-testid="stMetricValue"] { color: #1e3a8a !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (HERRAMIENTAS) ---
st.sidebar.title("🛠️ Facility Tools")
st.sidebar.markdown("---")

st.sidebar.subheader("📥 Input de Datos")
n_lote = st.sidebar.number_input("Cantidad de Piezas", 5, 50, 10)
t_proceso = st.sidebar.slider("Tiempo de Ciclo (s)", 0.5, 4.0, 1.5)

st.sidebar.subheader("💰 Parámetros Económicos")
costo_mat = st.sidebar.number_input("Costo Material ($)", 5.0, 50.0, 15.0)
precio_vta = st.sidebar.number_input("Precio Venta ($)", 20.0, 200.0, 80.0)

st.sidebar.subheader("📉 Análisis de Riesgo")
prob_error = st.sidebar.slider("Tasa de Fallo (%)", 0, 25, 5)

st.sidebar.markdown("---")
iniciar = st.sidebar.button("▶️ RUN SIMULATION", use_container_width=True)
reiniciar = st.sidebar.button("🔄 RESET SYSTEM", use_container_width=True)

# --- PANTALLA PRINCIPAL ---
st.title("🏭 Planta de Producción: Vista de Planta")
st.write("---")

if iniciar:
    # 1. KPIs Superiores
    k1, k2, k3, k4 = st.columns(4)
    met_util = k1.empty()
    met_yield = k2.empty()
    met_scrap = k3.empty()
    met_prog = k4.empty()

    st.write("### 🧩 Monitor de Línea")
    
    # 2. Medidores (Gauges)
    g1, g2, g3, g4, g5 = st.columns(5)
    gauge_a = g1.empty()
    gauge_b = g3.empty()
    gauge_c = g5.empty()

    # 3. Diseño de la Línea Física
    m_a, b1, m_b, b2, m_c = st.columns()

    with m_a:
        st.markdown('<div class="estacion">⚙️<br><b>DESPULPADO</b></div>', unsafe_allow_html=True)
        v_a = st.empty()

    v_b1 = b1.empty()

    with m_b:
        st.markdown('<div class="estacion">🌀<br><b>MOLIENDA</b></div>', unsafe_allow_html=True)
        v_b = st.empty()

    v_b2 = b2.empty()

    with m_c:
        st.markdown('<div class="estacion">📦<br><b>ENSACADO</b></div>', unsafe_allow_html=True)
        v_c = st.empty()

    log_historial = st.empty()

    # --- LÓGICA ---
    buenas, fallas, dinero, scrap = 0, 0, 0, 0
    historial = []

    for i in range(1, n_lote + 1):
        sku = f"P-{i}"
        
        # FASE 1
        gauge_a.markdown("<p class='gauge'>🔴 100%</p>", unsafe_allow_html=True)
        v_a.info(f"Ocupado: {sku}")
        time.sleep(t_proceso)
        gauge_a.markdown("<p class='gauge'>⚪ 0%</p>", unsafe_allow_html=True)
        v_a.write("Esperando...")

        # TRÁNSITO 1
        for d in [".", "..", "...", "📦", "...", "✔"]:
            v_b1.markdown(f"<div class='banda' style='text-align:center; color:white;'>{d}</div>", unsafe_allow_html=True)
            time.sleep(0.15)
        v_b1.markdown('<div class="banda"></div>', unsafe_allow_html=True)

        # FASE 2
        gauge_b.markdown("<p class='gauge'>🟧 100%</p>", unsafe_allow_html=True)
        v_b.warning(f"Ocupado: {sku}")
        time.sleep(t_proceso)
        gauge_b.markdown("<p class='gauge'>⚪ 0%</p>", unsafe_allow_html=True)
        v_b.write("Esperando...")

        # TRÁNSITO 2
        for d in [".", "..", "...", "📦", "...", "✔"]:
            v_b2.markdown(f"<div class='banda' style='text-align:center; color:white;'>{d}</div>", unsafe_allow_html=True)
            time.sleep(0.15)
        v_b2.markdown('<div class="banda"></div>', unsafe_allow_html=True)

        # FASE 3
        error = (np.random.random() * 100) < prob_error
        costo_pz = costo_mat + (t_proceso * 2 * 1.5)
        
        if error:
            fallas += 1
            scrap += costo_pz
            v_c.error(f"❌ FALLO")
            res = "RECHAZADA"
        else:
            buenas += 1
            ganancia = precio_vta - costo_pz
            dinero += ganancia
            v_c.success(f"✅ OK")
            res = "OK"

        # ACTUALIZAR KPIs
        met_util.metric("Utilidad Neta", f"${round(dinero, 2)}")
        met_yield.metric("OEE (Calidad)", f"{round((buenas/i)*100, 1)}%")
        met_scrap.metric("Costo Scrap", f"${round(scrap, 2)}", delta_color="inverse")
        met_prog.metric("Avance", f"{i}/{n_lote}")

        historial.append({"SKU": sku, "Estado": res, "Margen": round(precio_vta - costo_pz if not error else -costo_pz, 2)})
        log_historial.dataframe(pd.DataFrame(historial).tail(5), use_container_width=True)

    st.balloons()

elif reiniciar:
    st.rerun()

else:
    st.info("👈 Configura los parámetros en el panel de herramientas y presiona 'RUN SIMULATION'")
