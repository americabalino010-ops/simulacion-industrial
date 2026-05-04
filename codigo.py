import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Factory Architect V29", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .estacion-box { 
        background-color: #ffffff; 
        border: 3px solid #1e3a8a; 
        border-radius: 12px; 
        padding: 15px; 
        text-align: center; 
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    h1, h2, h3 { color: #1e3a8a !important; font-weight: bold; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 10px; border: 1px solid #dee2e6; }
    </style>
    """, unsafe_allow_html=True)

# --- PANEL DE DISEÑO (SIDEBAR) ---
st.sidebar.title("🏗️ Factory Architect")
st.sidebar.markdown("---")

# 1. Selección de Estaciones
st.sidebar.subheader("📐 Diseño de Línea")
estaciones_seleccionadas = st.sidebar.multiselect(
    "Añade estaciones a tu flujo:",
    ["Corte CNC", "Pulido", "Pintura", "Ensamble", "Inspección"],
    default=["Corte CNC", "Ensamble"]
)

# 2. Configuración Individual por Estación
config_estaciones = {}
if estaciones_seleccionadas:
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Ajustes por Estación")
    for est in estaciones_seleccionadas:
        with st.sidebar.expander(f"Parámetros: {est}"):
            t_ciclo = st.slider(f"Tiempo de Ciclo (s) - {est}", 0.5, 5.0, 2.0, key=f"t_{est}")
            p_error = st.slider(f"Tasa de Fallo (%) - {est}", 0, 20, 2, key=f"e_{est}")
            config_estaciones[est] = {"tiempo": t_ciclo, "error": p_error}

# 3. Parámetros Globales
st.sidebar.markdown("---")
st.sidebar.subheader("💰 Parámetros Económicos")
n_lote = st.sidebar.number_input("Lote de Producción", 5, 50, 10)
c_mat = st.sidebar.number_input("Costo Materia Prima ($)", 10.0, 100.0, 25.0)
v_precio = st.sidebar.number_input("Precio Venta Final ($)", 50.0, 500.0, 150.0)

# --- PANTALLA PRINCIPAL ---
st.title("🏭 Constructor de Planta Dinámico")

if not estaciones_seleccionadas:
    st.info("👈 Selecciona estaciones en el panel izquierdo para comenzar a diseñar tu planta.")
else:
    # Mostrar el flujo diseñado
    st.write(f"### 🧬 Secuencia de Producción: {' ⮕ '.join(estaciones_seleccionadas)}")
    
    if st.sidebar.button("▶️ EJECUTAR SIMULACIÓN PERSONALIZADA", use_container_width=True):
        # Contenedores de KPIs
        k1, k2, k3, k4 = st.columns(4)
        met_util = k1.empty()
        met_oee = k2.empty()
        met_scrap = k3.empty()
        met_prog = k4.empty()

        st.write("---")
        
        # Dibujar Layout de Planta
        columnas_viz = st.columns(len(estaciones_seleccionadas))
        placeholder_viz = []
        for idx, est in enumerate(estaciones_seleccionadas):
            with columnas_viz[idx]:
                st.markdown(f'<div class="estacion-box"><b>{est}</b></div>', unsafe_allow_html=True)
                placeholder_viz.append(st.empty())

        # --- LÓGICA DE SIMULACIÓN ---
        utilidad_total, scrap_total, buenas = 0, 0, 0
        historial = []

        for i in range(1, n_lote + 1):
            sku = f"PZ-{i}"
            costo_acumulado = c_mat
            fallo_en_pieza = False
            
            # Recorrido por cada estación diseñada
            for idx, est in enumerate(estaciones_seleccionadas):
                placeholder_viz[idx].info(f"Procesando {sku}...")
                
                # Cálculos basados en los sliders del usuario
                t_est = config_estaciones[est]["tiempo"]
                e_est = config_estaciones[est]["error"]
                
                # Cada segundo de máquina cuesta $2.0 (Energía/Mano de Obra)
                costo_acumulado += (t_est * 2.0)
                
                time.sleep(1) # Simulación de tiempo visual
                
                # Verificar si falla en esta estación
                if (np.random.random() * 100) < e_est:
                    fallo_en_pieza = True
                    placeholder_viz[idx].error("❌ FALLO")
                    break # Se detiene el proceso si falla
                else:
                    placeholder_viz[idx].success("✅ LISTO")

            # Resultado Final
            if fallo_en_pieza:
                scrap_total += costo_acumulado
                res = "RECHAZADA"
            else:
                buenas += 1
                utilidad_total += (v_precio - costo_acumulado)
                res = "OK"

            # Actualizar KPIs
            met_util.metric("Utilidad Neta", f"${round(utilidad_total, 2)}")
            met_oee.metric("Calidad (Yield)", f"{round((buenas/i)*100, 1)}%")
            met_scrap.metric("Costo Scrap", f"${round(scrap_total, 2)}", delta_color="inverse")
            met_prog.metric("Avance", f"{i}/{n_lote}")
            
            historial.append({"SKU": sku, "Estado": res, "Costo Final": round(costo_acumulado, 2)})
            time.sleep(0.5)

        st.balloons()
        st.write("### 📝 Reporte de Diseño de Línea")
        st.dataframe(pd.DataFrame(historial), use_container_width=True)
