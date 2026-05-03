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
        # Guardamos los valores para usarlos en la siguiente faceta
        st.session_state.datos_sim = {
            "c_mat": c_mat, "c_seg": c_seg, "p_vta": p_vta,
            "n_lote": n_lote, "t_ciclo": t_ciclo, "fallo_p": fallo_p
        }
        cambiar_faceta('simulacion')
    
    if st.button("⬅️ Volver"):
        cambiar_faceta('presentacion')

# --- FACETA 3: SIMULACIÓN Y RESULTADOS (VERSIÓN FINAL CON DESCARGA) ---
elif st.session_state.faceta == 'simulacion':
    d = st.session_state.datos_sim
    st.title("📊 Monitor de Producción en Vivo")
    
    # Dashboard de KPIs
    c1, c2, c3 = st.columns(3)
    met_util = c1.empty()
    met_oee = c2.empty()
    met_prog = c3.empty()

    # Layout de la planta
    st.write("---")
    col_a, col_b, col_c = st.columns(3) 
    v_corte = col_a.empty()
    v_trans = col_b.empty()
    v_ensam = col_c.empty()
    
    log_eventos = st.empty()

    # Variables para el reporte y lógica
    historial = []
    buenas, fallas, dinero = 0, 0, 0
    
    for i in range(1, int(d['n_lote']) + 1):
        sku = f"PZ-{100+i}"
        costo_pz = d['c_mat']
        
        # 1. Fase de Corte
        v_corte.info(f"🗜️ **CORTE**\n\nProcesando: {sku}")
        v_trans.write("---")
        v_ensam.write("---")
        time.sleep(d['t_ciclo'])
        costo_pz += (d['t_ciclo'] * d['c_seg'])
        
        # 2. Fase de Tránsito
        v_corte.success("🗜️ **CORTE**\n\nEsperando...")
        v_trans.warning(f"🚚 **MOVIMIENTO**\n\n{sku}")
        time.sleep(1)
        
        # 3. Fase de Ensamble
        v_trans.write("---")
        v_ensam.info(f"🤖 **ENSAMBLE**\n\nProcesando: {sku}")
        time.sleep(d['t_ciclo'])
        costo_pz += (d['t_ciclo'] * d['c_seg'])
        
        # Calidad y Resultados
        v_ensam.success("🤖 **ENSAMBLE**\n\nListo")
        error = (np.random.random() * 100) < d['fallo_p']
        
        if error:
            res = "RECHAZADA"
            fallas += 1
            ganancia_pz = 0
            log_eventos.error(f"❌ {sku} RECHAZADA. Pérdida: ${round(costo_pz, 2)}")
        else:
            res = "OK"
            buenas += 1
            ganancia_pz = d['p_vta'] - costo_pz
            dinero += ganancia_real = ganancia_pz
            log_eventos.success(f"✅ {sku} OK. Utilidad: ${round(ganancia_pz, 2)}")
        
        # Guardar en historial para el CSV
        historial.append({
            "SKU": sku, 
            "Estado": res, 
            "Costo Acumulado ($)": round(costo_pz, 2), 
            "Utilidad Real ($)": round(ganancia_pz, 2)
        })
        
        # Actualizar KPIs
        met_util.metric("Utilidad Neta", f"${round(dinero, 2)}")
        met_oee.metric("Calidad (OEE)", f"{round((buenas/i)*100, 1)}%")
        met_prog.metric("Progreso", f"{i}/{int(d['n_lote'])}")
        
        time.sleep(0.5)

    st.balloons()
    st.success("✅ Turno de producción finalizado.")

    # --- SECCIÓN DE DESCARGA Y REINICIO ---
    df_final = pd.DataFrame(historial)
    csv = df_final.to_csv(index=False).encode('utf-8')
    
    st.write("### 📂 Acciones de Fin de Turno")
    c_down, c_reset = st.columns(2)
    
    with c_down:
        st.download_button(
            label="📥 Descargar Reporte Excel (CSV)",
            data=csv,
            file_name=f"reporte_produccion_{time.strftime('%Y%m%d-%H%M')}.csv",
            mime="text/csv",
        )
    
    with c_reset:
        if st.button("🔄 Reiniciar Sistema"):
            st.session_state.faceta = 'presentacion'
            st.rerun()
