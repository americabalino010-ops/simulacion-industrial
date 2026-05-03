import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Industrial Control v19", layout="wide")
st.title("🏭 Monitor Industrial: Flujo de Procesos y OEE")

# --- PARÁMETROS FINANCIEROS Y TÉCNICOS (SIDEBAR) ---
st.sidebar.header("💰 Configuración Económica")
costo_material = st.sidebar.number_input("Costo Material ($/pz)", 5.0, 100.0, 20.0)
costo_segundo = st.sidebar.number_input("Costo Operativo ($/seg)", 0.1, 10.0, 1.5)
precio_venta = st.sidebar.number_input("Precio de Venta ($/pz)", 10.0, 500.0, 100.0)

st.sidebar.header("⚙️ Parámetros de Línea")
lote = st.sidebar.number_input("Lote de Producción", 5, 50, 10)
t_maquina = st.sidebar.slider("Tiempo de Ciclo (seg)", 1, 5, 2)
tasa_fallo = st.sidebar.slider("Probabilidad de Error (%)", 0, 30, 5)

# --- DISEÑO DEL DASHBOARD ---
col_layout, col_calculos = st.columns([2, 1])

with col_layout:
    st.subheader("📍 Planta en Tiempo Real")
    estaciones = st.columns(3)
    c_corte = estaciones[0].empty()
    c_trans = estaciones[1].empty()
    c_ensam = estaciones[2].empty()
    status_text = st.empty()

with col_calculos:
    st.subheader("🧾 Desglose de Costos (Pieza Actual)")
    area_calculo = st.empty()
    st.write("---")
    met_utilidad = st.empty()
    met_oee = st.empty()

# --- LÓGICA DE SIMULACIÓN ---
if st.sidebar.button("▶️ INICIAR PRODUCCIÓN"):
    utilidad_neta, total_costo_scrap, buenas, fallas = 0, 0, 0, 0
    historial = []

    for i in range(1, lote + 1):
        sku = f"PZ-{100 + i}"
        costo_acumulado = costo_material
        
        # 1. CORTE
        c_corte.info("🗜️ CORTE\nPROCESANDO")
        c_trans.write("---")
        c_ensam.write("---")
        
        for t in range(t_maquina):
            costo_acumulado += costo_segundo
            status_text.write(f"⚙️ {sku}: Fase de Corte...")
            area_calculo.markdown(f"**Material:** ${costo_material}  \n**Energía/MO:** ${round(costo_acumulado-costo_material,2)}  \n**SUBTOTAL:** ${round(costo_acumulado,2)}")
            time.sleep(1)

        # 2. TRÁNSITO
        c_corte.write("🗜️ LIBRE")
        c_trans.warning(f"🚚 {sku}\nEN MOVIMIENTO")
        time.sleep(1)

        # 3. ENSAMBLE
        c_trans.write("---")
        c_ensam.info("🤖 ENSAMBLE\nPROCESANDO")
        for t in range(t_maquina):
            costo_acumulado += costo_segundo
            status_text.write(f"🔧 {sku}: Fase de Ensamble...")
            area_calculo.markdown(f"**Material:** ${costo_material}  \n**Energía/MO:** ${round(costo_acumulado-costo_material,2)}  \n**SUBTOTAL:** ${round(costo_acumulado,2)}")
            time.sleep(1)

        # 4. RESULTADO Y CALIDAD
        error = (np.random.random() * 100) < tasa_fallo
        if error:
            fallas += 1
            total_costo_scrap += costo_acumulado
            status_text.error(f"❌ {sku} RECHAZADA. Pérdida: ${round(costo_acumulado, 2)}")
        else:
            buenas += 1
            ganancia_pz = precio_venta - costo_acumulado
            utilidad_neta += ganancia_pz
            status_text.success(f"✅ {sku} APROBADA. Utilidad: ${round(ganancia_pz, 2)}")

        # --- ACTUALIZAR MÉTRICAS ---
        oee_actual = (buenas / i) * 100
        met_utilidad.metric("Utilidad Acumulada", f"${round(utilidad_neta, 2)}", f"-${round(total_costo_scrap,2)} Scrap")
        met_oee.metric("OEE (Calidad)", f"{round(oee_actual, 1)}%", help="Disponibilidad x Rendimiento x Calidad")
        
        time.sleep(1)

    st.balloons()
    st.success(f"🏁 Turno completado. OEE Final: {round((buenas/lote)*100, 1)}%")
